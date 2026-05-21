import network
import urequests
import time
import gc
import json


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
    print('Connecting to WiFi...')
    time.sleep(1)

print('Connected! IP:', wlan.ifconfig()[0])

gc.collect()

SERVER_IP = env.get("SERVER_IP")
url = f"http://{SERVER_IP}/test"


response = ""

def try_connection():
    print("sending request")
    response = urequests.get(url)
    print("Response:", response.text)

try:
    try_connection()
except Exception as e:
    print("Error sending request:", e)

wlan.disconnect()
