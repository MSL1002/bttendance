"""
Pico W RFID Reader
Reads RFID card UIDs and prints them to serial
"""

from mfrc522 import MFRC522
from machine import Pin
import time

# Initialize RFID reader with correct pins
# SCK=6, MOSI=7, MISO=4, RST=8, CS=27
reader = MFRC522(6, 7, 4, 8, 27)

print("RFID Reader Initialized")
print("Waiting for RFID cards...")
print("-" * 40)

last_uid = None
last_read_time = 0

while True:
    try:
        # Check if a card is present
        stat, tag_type = reader.request(reader.REQIDL)
        
        if stat == reader.OK:
            # Card detected, try to read UID
            result = reader.anticoll()
            
            # anticoll returns multiple values, get just the UID part
            if len(result) >= 2:
                stat = result[0]
                uid = result[1]
                
                if stat == reader.OK:
                    uid_str = str(uid)
                    current_time = time.time()
                    
                    # Only print if new card or enough time has passed
                    if uid_str != last_uid or (current_time - last_read_time) > 1.0:
                        print("UID: " + uid_str)
                        last_uid = uid_str
                        last_read_time = current_time
        
        time.sleep(0.1)
        
    except KeyboardInterrupt:
        print("Stopped")
        break
    except Exception as e:
        print("Error: " + str(e))