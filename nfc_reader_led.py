import RPi.GPIO as GPIO
import board
import neopixel
from time import time

from pn532 import *

pixels = neopixel.NeoPixel(board.D18, 1)

def pulsate(color, duration):
    start_time = time()
    while time() - start_time < duration:
        for i in range(0, 101):
            pixels[0] = (int(color[0] * i / 100), int(color[1] * i / 100), int(color[2] * i / 100))
            uid = read_nfc_tag()
            if uid:  # Check for NFC tag
                return uid
        for i in range(100, -1, -1):
            pixels[0] = (int(color[0] * i / 100), int(color[1] * i / 100), int(color[2] * i / 100))
            uid = read_nfc_tag()
            if uid:  # Check for NFC tag
                return uid
    return None

def read_nfc_tag():
    uid = pn532.read_passive_target(timeout=0.5)
    if uid:
        print('Found card with UID:', [hex(i) for i in uid])
        return uid
    return None

if __name__ == '__main__':
    try:
        pn532 = PN532_SPI(debug=False, reset=20, cs=4)
        #pn532 = PN532_I2C(debug=False, reset=20, req=16)
        #pn532 = PN532_UART(debug=False, reset=20)

        ic, ver, rev, support = pn532.get_firmware_version()
        print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))

        # Configure PN532 to communicate with MiFare cards
        pn532.SAM_configuration()

        print('Waiting for RFID/NFC card...')
        while True:
            uid = pulsate((255, 0, 0), 5)  # Red color
            if uid is None:
                continue
            # If a card was found, turn the LED green
            pixels[0] = (0, 255, 0)
            print('Found card with UID:', [hex(i) for i in uid])
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
