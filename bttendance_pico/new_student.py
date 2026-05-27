from mfrc522 import MFRC522
from machine import Pin
import network
import urequests
import time
import gc
import json

reader = MFRC522(spi_id=0, sck=6, miso=4, mosi=7, cs=5, rst=22)
LED = Pin("LED", Pin.OUT)

with open("env.json") as f:
    env = json.load(f)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(env["SSID"], env["PASSWORD"])

while not wlan.isconnected():
    print("Connecting to WiFi...")
    LED.toggle()
    time.sleep(1)

print("Connected! IP:", wlan.ifconfig()[0])
LED.on()
print("Ready — scan a card to enroll")

while True:
    reader.init()
    (stat, tag_type) = reader.request(reader.REQIDL)
    if stat == reader.OK:
        (stat, uid) = reader.SelectTagSN()
        if stat == reader.OK:
            rfid = int.from_bytes(bytes(uid), "little", False)
            url = f"http://{env['SERVER_IP']}:{env['SERVER_PORT']}/enroll-rfid?rfid={rfid}"
            try:
                r = urequests.post(url)
                print("Response:", r.text)
                r.close()
                LED.off()
            except Exception as e:
                print("Error:", e)
            gc.collect()
            break
    time.sleep(0.5)

wlan.disconnect()
