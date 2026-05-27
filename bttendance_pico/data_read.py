'''

This needs to get an RFID + collaberate with the front end to input a student into the DB

take in RFID from here
take in first name, last name, and student ID from website

potential solution:

Admin inputs student info on website
website waits until it gets a POST from the pico

Specialized Pico (with this file as it's main.py) posts to special endpoint to add the RFID to the student

Once we get the RFID, we wrap the student info up
enter it into the DB

return website to home page
make scanner await another scan

'''

from mfrc522 import MFRC522
import time

reader = MFRC522(spi_id=0,sck=6,miso=4,mosi=7,cs=5,rst=22)

print("scan an ID...")
print("")

while True:
    reader.init()
    (stat, tag_type) = reader.request(reader.REQIDL)
    if stat == reader.OK:
        (stat, uid) = reader.SelectTagSN()
        if stat == reader.OK:
            card = int.from_bytes(bytes(uid),"little",False)
            print("CARD ID: "+str(card))
    time.sleep(.5)