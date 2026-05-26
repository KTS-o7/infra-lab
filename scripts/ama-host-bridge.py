import json
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer


class BridgeHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/run":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            command = data.get("command")
            prompt = data.get("prompt")

            print(f"Executing: {command} {prompt!r}")

            try:
                result = subprocess.run(
                    f"{command} {prompt!r}",
                    shell=True,
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
    server_address = ("", port)
    httpd = HTTPServer(server_address, BridgeHandler)
    print(f"AMA Host Bridge listening on port {port}...")
    print("This allows the containerized API to run commands in your local terminal.")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
