from mfrc522 import MFRC522
from machine import Pin
import network
import urequests
import time
import gc
import json

reader = MFRC522(spi_id=0,sck=6,miso=4,mosi=7,cs=5,rst=22)
LED = Pin("LED", Pin.OUT)

def flash_LED(num_flashes):
    for i in range(num_flashes):
        LED.toggle()
        time.sleep(.5)
        LED.toggle()


with open("env.json") as f:
    env = json.load(f)
    
# WiFi credentials
SSID = env.get("SSID")
PASSWORD = env.get("PASSWORD")

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

wlan.connect(SSID, PASSWORD)

try:
    while not wlan.isconnected():
        print('Attempting to Connect to WiFi...')
        LED.toggle()
        time.sleep(1)

    print('Connected! IP:', wlan.ifconfig()[0])
    LED.off()

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
                SERVER_PORT = env.get("SERVER_PORT")
                url = f"http://{SERVER_IP}:{SERVER_PORT}/log-scan?rfid={rfid}&location={env.get("LOCATION")}"

                def try_connection():
                    print("sending request")
                    response = urequests.post(url)
                    print("Response", response.text)
                    return response.text

                try:
                    output = try_connection()
                    flash_LED(2)
                    #if card not found, try to input the card into the DB as a student
                    if output == "RFID not found in database.":
                        url = f"http://{env['SERVER_IP']}:{env['SERVER_PORT']}/enroll-rfid?rfid={rfid}"
                        try_connection()
                    
                except Exception as e:
                    print("Error sending request:", e)
                    flash_LED(5)

                
                time.sleep(1)
                
                print("Awaiting ID")
                print("")

                
        gc.collect()
finally:
    print("performing clean up...")
    wlan.disconnect()
    LED.off()
    print("clean up OK.")
