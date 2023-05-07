# SPDX-FileCopyrightText: 2022 Liz Clark for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import os
import time
import ipaddress
import wifi
import socketpool
import board
import microcontroller


from digitalio import DigitalInOut, Direction
from adafruit_httpserver.server import HTTPServer
from adafruit_httpserver.request import HTTPRequest
from adafruit_httpserver.response import HTTPResponse
from adafruit_httpserver.methods import HTTPMethod
from adafruit_httpserver.mime_type import MIMEType


#  onboard LED setup
led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT
led.value = False



#  connect to network
print()
print("Connecting to WiFi")


#  set static IP address
ipv4 =  ipaddress.IPv4Address("192.168.1.42")
netmask =  ipaddress.IPv4Address("255.255.255.0")
gateway =  ipaddress.IPv4Address("192.168.1.1")
wifi.radio.set_ipv4_address(ipv4=ipv4,netmask=netmask,gateway=gateway)

#  connect to your SSID
wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))

print("Connected to WiFi")
pool = socketpool.SocketPool(wifi.radio)
server = HTTPServer(pool, "/static")


#  font for HTML
font_family = "monospace"

#  the HTML script
#  setup as an f string
#  this way, can insert string variables from code.py directly
#  of note, use {{ and }} if something from html *actually* needs to be in brackets
#  i.e. CSS style formatting
def webpage():
    html = f"""
    <!DOCTYPE html>
    <html>
        <head>
        <meta http-equiv="Content-type" content="text/html;charset=utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            html {{
                font-family: {font_family };
                background-color: lightgrey;
                display:inline-block;
                margin: 0px auto;
                text-align: center;
            }}

            h1 {{
                color: deeppink;
                width: 200;
                word-wrap: break-word;
                padding: 2vh;
                font-size: 35px;
            }}

            p {{
                font-size: 1.5rem;
                width: 200;
                word-wrap: break-word;
            }}

            .button {{
                font-family: {font_family};
                display: inline-block;
                background-color: black;
                border: none;
                border-radius: 4px;
                color: white;
                padding: 16px 40px;
                text-decoration: none;
                font-size: 30px;
                margin: 2px;
                cursor: pointer;
            }}

            p.dotted {{
                margin: auto;
                width: 75%;
                font-size: 25px;
                text-align: center;
            }}
        </style>
        </head>
        <body>
        <title>Pico W HTTP Server</title>
        <h1>Pico W HTTP Server</h1>
    
        <h1>Control the onboard LED with these buttons:</h1>
        
        <form accept-charset="utf-8" method="POST">
            <button class="button" name="LED ON" value="ON" type="submit">LED ON</button>
        </form>
        <p>
        <form accept-charset="utf-8" method="POST">
            <button class="button" name="LED OFF" value="OFF" type="submit">LED OFF</button>
        </form>
        </body>
    </html>
    """
    return html

#  route default static IP
@server.route("/")
def base(request: HTTPRequest):  # pylint: disable=unused-argument
    #  serve the HTML f string
    #  with content type text/html
    with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
        response.send(f"{webpage()}")

#  if a button is pressed on the webpage
@server.route("/", method=HTTPMethod.POST)
def buttonpress(request: HTTPRequest):
    #  get the raw text
    raw_text = request.raw_request.decode("utf8")
    print(raw_text)
    if "ON" in raw_text:                    # if the led on button was pressed  turn on the onboard LED
        led.value = True

    if "OFF" in raw_text:                   # if the led off button was pressed turn the onboard LED off
        led.value = False
   
    #  reload site
    with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
        response.send(f"{webpage()}")

print("starting server..")
# startup the server
try:
    server.start(str(wifi.radio.ipv4_address))
    print("Listening on http://%s:80" % wifi.radio.ipv4_address)
#  if the server fails to begin, restart the pico w
except OSError:
    time.sleep(5)
    print("restarting..")
    microcontroller.reset()
ping_address = ipaddress.ip_address("8.8.4.4")


while True:
    try:
        #  every 30 seconds, ping server 
        if (clock + 30) < time.monotonic():
            if wifi.radio.ping(ping_address) is None:
                connect_text_area.text = "Disconnected!"
                ssid_text_area.text = None
                print("lost connection")
            else:
                connect_text_area.text = "Connected to:"
                ssid_text_area.text = "%s" % os.getenv('WIFI_SSID')
                print("connected")
            clock = time.monotonic()
        #  poll the server for incoming/outgoing requests
        server.poll()
    # pylint: disable=broad-except
    except Exception as e:
        print(e)
        continue
