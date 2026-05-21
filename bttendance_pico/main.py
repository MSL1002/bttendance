#REAL MAIN TIME!!!

'''
What does this need to do?

connect to backend http server over WiFi

if connection drops:
    print error(s)
    flash light
    retry connection

loop until we get a scan

take scan's ID, put scan in DB as clock in (flask handles this)

loop until we get another scan, etc...

'''

from mfrc522 import MFRC522
from machine import Pin
import network
import urequests
import time
import gc
import json

reader = MFRC522(spi_id=0,sck=6,miso=4,mosi=7,cs=5,rst=22)


with open("env.json") as f:
    env = json.load(f)

# WiFi credentials
SSID = env.get("SSID")
PASSWORD = env.get("PASSWORD")

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

while not wlan.isconnected():
    print('Attempting to Connect to WiFi...')
    Pin("LED", Pin.OUT).value(1);
    time.sleep(1)

print('Connected! IP:', wlan.ifconfig()[0])
Pin("LED", Pin.OUT).value(0);

print("Awaiting ID")
print("")

while True:
    reader.init()
    (stat, tag_type) = reader.request(reader.REQIDL)
    if stat == reader.OK:
        (stat, uid) = reader.SelectTagSN()
        if stat == reader.OK:
            rfid = int.from_bytes(bytes(uid),"little",False)

            SERVER_IP = env.get("SERVER_IP")
            url = f"http://{SERVER_IP}/log-scan?rfid={rfid}&location={env.get("LOCATION")}"

            def try_connection():
                print("sending request")
                response = urequests.post(url)
                print("Response:", response.text,"\n")

            try:
                try_connection()
                Pin("LED", Pin.OUT).value(1);
                time.sleep(1)
                Pin("LED", Pin.OUT).value(0);
            except Exception as e:
                print("Error sending request:", e)

            time.sleep(1)
            
            print("Awaiting ID")
            print("")

            
    gc.collect()