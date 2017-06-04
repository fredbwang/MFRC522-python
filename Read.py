#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import MFRC522
import signal
import time
import json
import os

continue_reading = True


# Capture SIGINT for cleanup when the script is aborted
def end_read(signal, frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False
    GPIO.cleanup()


# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Welcome message
print "Welcome to the MFRC522 data read example"
print "Press Ctrl-C to stop."

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:
    time.sleep(1)
    # Scan for cards
    (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:
        print "Card detected"

    # Get the UID of the card
    (status, uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:

        # Print UID
        print "Card read UID: " + str(uid[0]) + "," + str(uid[1]) + "," + str(uid[2]) + "," + str(uid[3])

        # This is the default key for authentication
        key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

        # Select the scanned tag
        MIFAREReader.MFRC522_SelectTag(uid)

        # Authenticate
        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)

        # Check if authenticated
        if status == MIFAREReader.MI_OK:
            MIFAREReader.MFRC522_Read(8)
            MIFAREReader.MFRC522_StopCrypto1()
        else:
            print "Authentication error"

    # flag: whether there is data.json. not used
    isData = 0

    # check if dir /data and json file data.json exists
    path = os.getcwd()
    print path, type(path)
    print os.path.exists(path + '/data')
    if os.path.exists(path + '/data'):
        if os.path.exists(path + '/data/data.json'):
            print 'reading RFID.'
            # should extend json
            with open('data/data.json', 'rb') as infile:
                data = json.load(infile)
        else:
            print 'creating file data.json'
            # should write_json
            data = {}
    else:
        print 'creating dir /data'
        os.makedirs(path + '/data')
        data = {}

    # get all the items in data
    items = data.keys()

    # if this id is not in item ids create an item(key) in the dict
    uidkey = str(uid[0]) + str(uid[1]) + str(uid[2]) + str(uid[3]) + str(uid[4])
    print uidkey
    if uidkey not in items:
        data[uidkey] = [time.time(), 1]
    else:
        data[uidkey] = [time.time(), data[uidkey][1] * -1]
    if data[uidkey] == 1:
        print uidkey, 'entering room'
    else:
        print uidkey, 'leaving room'
    with open('data/data.json', 'w') as infile:
        infile.write(json.dumps(data))

