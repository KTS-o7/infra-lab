import asyncio
import fcntl
import json
import logging
import os
import pty
import struct
import subprocess
import termios

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

# Configure logging to help diagnose container issues
logger = logging.getLogger("terminal")
logger.setLevel(logging.INFO)

router = APIRouter(prefix="/terminal", tags=["terminal"])


@router.websocket("/ws")
async def terminal_websocket(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection accepted")

    master_fd = None
    p = None
    # REVIEW FIX (Sarang): Initialize loop=None here alongside master_fd so the
    # finally block can safely guard with `if loop is not None`. If loop were
    # only assigned inside the try block and an exception fired before that line,
    # the finally would raise NameError when it tried to call loop.remove_reader().
    loop = None

    try:
        # Spawn shell in pty
        master_fd, slave_fd = pty.openpty()

        # Set default terminal size
        buf = struct.pack("HHHH", 24, 80, 0, 0)
        fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, buf)

        env = os.environ.copy()
        env["TERM"] = "xterm-256color"
        # Inside the container, localhost:4566 fails. We point to the internal floci service.
        env["AWS_ENDPOINT_URL"] = os.getenv("AWS_ENDPOINT_URL", "http://floci:4566")
        cwd = os.getcwd()

        # REVIEW FIX (Sarang): Wrap Popen + slave_fd close in try/finally so
        # slave_fd is never leaked if Popen raises (e.g. /bin/bash not found).
        # Without this, the open slave_fd would persist until garbage collection,
        # blocking the PTY from ever receiving EOF.
        try:
            p = subprocess.Popen(
                ["/bin/bash"],
                preexec_fn=os.setsid,
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                env=env,
                cwd=cwd,
            )
        finally:
            # Close slave_fd in parent process — must happen even if Popen fails
            os.close(slave_fd)

        # Set master_fd to non-blocking
        fl = fcntl.fcntl(master_fd, fcntl.F_GETFL)
        fcntl.fcntl(master_fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        # REVIEW FIX (Sarang): Use get_running_loop() instead of get_event_loop().
        # get_event_loop() is deprecated in Python 3.10+ and emits a DeprecationWarning
        # when there is no current event loop set in the thread. Inside an async
        # function we are always running inside a loop, so get_running_loop() is
        # both correct and explicit.
        loop = asyncio.get_running_loop()
        output_queue = asyncio.Queue()

        def on_pty_read():
            try:
                # REVIEW FIX (Sarang): Increase read buffer from 1024 to 65536 bytes.
                # A 1 KB buffer means high-throughput output (e.g. `cat large_file`)
                # requires hundreds of syscalls and read-loop iterations per second,
                # adding latency and CPU overhead. 64 KB matches common pipe/socket
                # buffer sizes and amortises that cost significantly.
                data = os.read(master_fd, 65536)
                if data:
                    output_queue.put_nowait(data)
                else:
                    # EOF
                    output_queue.put_nowait(None)
            except (IOError, OSError):
                output_queue.put_nowait(None)

        loop.add_reader(master_fd, on_pty_read)

        async def send_to_websocket():
            while True:
                data = await output_queue.get()
                if data is None:  # EOF signal
                    logger.info("PTY reached EOF, closing connection")
                    break
                try:
                    await websocket.send_bytes(data)
                except Exception as e:
                    logger.error(f"Error sending to websocket: {e}")
                    break

        async def receive_from_websocket():
            while True:
                try:
                    message = await websocket.receive()
                    if message["type"] == "websocket.disconnect":
                        logger.info("WebSocket disconnected by client")
                        break

                    if "text" in message:
                        try:
                            payload = json.loads(message["text"])
                            if payload.get("type") == "input":
                                os.write(master_fd, payload["data"].encode())
                            elif payload.get("type") == "resize":
                                rows = payload.get("rows", 24)
                                cols = payload.get("cols", 80)
                                buf = struct.pack("HHHH", rows, cols, 0, 0)
                                fcntl.ioctl(master_fd, termios.TIOCSWINSZ, buf)
                        except json.JSONDecodeError:
                            os.write(master_fd, message["text"].encode())
                    elif "bytes" in message:
                        os.write(master_fd, message["bytes"])
                except Exception as e:
                    logger.error(f"Error receiving from websocket: {e}")
                    break

        # Run both directions in parallel
        await asyncio.gather(send_to_websocket(), receive_from_websocket())

    except Exception as e:
        logger.error(f"Terminal backend error: {e}")
    finally:
        if master_fd is not None:
            # Guard with `if loop is not None` — see initialization comment above.
            if loop is not None:
                loop.remove_reader(master_fd)
            try:
                os.close(master_fd)
            except OSError:
                pass

        if p and p.poll() is None:
            p.terminate()

        logger.info("Terminal session cleaned up")
        try:
            await websocket.close()
        except Exception:
            pass
