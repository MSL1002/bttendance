# from mfrc522 import MFRC522
# reader = MFRC522(6, 7, 4, 8, 27)
# print("Reader created")

# # Try to detect a card
# for i in range(10):
#     stat, bits = reader.request(reader.REQIDL)
#     print("Attempt " + str(i) + ": status=" + str(stat) + " (OK=" + str(reader.OK) + ")")
#     if stat == reader.OK:
#         print("CARD DETECTED!")
#         print(str(uid))
#         break
#     import time
#     time.sleep(0.5)


from mfrc522 import MFRC522
reader = MFRC522(6, 7, 4, 8, 27)

stat, bits = reader.request(reader.REQIDL)
print("Request status: " + str(stat))

if stat == reader.OK:
    print("Card detected, attempting anticoll")
    stat2, uid = reader.anticoll()
    print(str(uid))