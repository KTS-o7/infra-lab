import json
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

# REVIEW FIX (Sarang): Max body size constant - 10KB is plenty for a chat message
MAX_BODY_SIZE = 10 * 1024  # 10KB


class BridgeHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/run":
            # REVIEW FIX (Sarang): Guard for missing/bad Content-Length header
            raw_length = self.headers.get("Content-Length")
            if raw_length is None:
                self.send_response(411)  # Length Required
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Content-Length header required"}).encode())
                return
            try:
                content_length = int(raw_length)
            except ValueError:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid Content-Length header"}).encode())
                return

            # REVIEW FIX (Sarang): Reject bodies exceeding MAX_BODY_SIZE to prevent memory exhaustion
            if content_length > MAX_BODY_SIZE:
                self.send_response(413)  # Payload Too Large
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"Request body exceeds {MAX_BODY_SIZE} byte limit"}).encode())
                return

            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            command = data.get("command")
            prompt = data.get("prompt")

            # REVIEW FIX (Sarang): Validate that command is not empty before use
            if not command:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Missing required field: command"}).encode())
                return

            print(f"Executing: {command} {prompt!r}")

            try:
                # REVIEW FIX (Sarang): Use list form with shell=False to prevent shell injection.
                # `command` comes from trusted config; `prompt` is user content passed as a
                # discrete argument - no shell interpolation occurs.
                result = subprocess.run(
                    [command, prompt],
                    shell=False,
                    capture_output=True,
                    text=True,
                    timeout=90,
                )
                if result.returncode == 0:
                    output = result.stdout.strip()
                    status = 200
                else:
                    output = f"CLI Error: {result.stderr.strip()}"
                    status = 200  # Return 200 so the UI can show the CLI error message
                response = {"output": output}
            except subprocess.TimeoutExpired:
                response = {
                    "output": "Timeout: The AI agent took too long to respond (90s limit)."
                }
                status = 200
            except Exception as e:
                response = {"error": str(e)}
                status = 500

            self.send_response(status)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())


def run(port=8080):
    # REVIEW FIX (Sarang): Bind to loopback only - never expose this service to the network
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, BridgeHandler)
    # REVIEW FIX (Sarang): Startup warning - make it clear this runs on the HOST and must stay local
    print("=" * 70)
    print("WARNING: AMA Host Bridge is running on the HOST machine.")
    print("It executes commands with your local user privileges.")
    print("NEVER expose this service to the network or a public interface.")
    print(f"Listening on 127.0.0.1:{port} (loopback only).")
    print("=" * 70)
    httpd.serve_forever()


if __name__ == "__main__":
    run()
