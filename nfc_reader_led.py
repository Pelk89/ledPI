import RPi.GPIO as GPIO
import board
import neopixel
from time import time
from multiprocessing import Process, Value
from ctypes import c_bool

from pn532 import *

pixels = neopixel.NeoPixel(board.D18, 32)

def pulsate(color, duration, run_pulsate):
    start_time = time()
    while time() - start_time < duration and run_pulsate.value:
        for i in range(0, 101):
            for j in range(len(pixels)):
                pixels[j] = (int(color[0] * i / 100), int(color[1] * i / 100), int(color[2] * i / 100))
        for i in range(100, -1, -1):
            for j in range(len(pixels)):
                pixels[j] = (int(color[0] * i / 100), int(color[1] * i / 100), int(color[2] * i / 100))

def read_nfc_tag(run_pulsate):
    while run_pulsate.value:
        uid = pn532.read_passive_target(timeout=0.5)
        if uid:
            print('Found card with UID:', [hex(i) for i in uid])
            run_pulsate.value = False
            for i in range(len(pixels)):
                pixels[i] = (0, 255, 0)
            break

if __name__ == '__main__':
    try:
        pn532 = PN532_SPI(debug=False, reset=20, cs=4)

        ic, ver, rev, support = pn532.get_firmware_version()
        print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))

        # Configure PN532 to communicate with MiFare cards
        pn532.SAM_configuration()

        print('Waiting for RFID/NFC card...')
        run_pulsate = Value(c_bool, True)
        pulsate_process = Process(target=pulsate, args=((255, 255, 255), 5, run_pulsate))
        read_nfc_process = Process(target=read_nfc_tag, args=(run_pulsate,))

        pulsate_process.start()
        read_nfc_process.start()

        pulsate_process.join()
        read_nfc_process.join()
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
