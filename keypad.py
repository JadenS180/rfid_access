import RPi.GPIO as GPIO
import time
from config import ROW_PINS, COL_PINS, KEYPAD

def init_keypad():
    GPIO.setmode(GPIO.BCM)
    for row in ROW_PINS:
        GPIO.setup(row, GPIO.OUT)
        GPIO.output(row, GPIO.HIGH)
    for col in COL_PINS:
        GPIO.setup(col, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def read_key():
    for i, row in enumerate(ROW_PINS):
        GPIO.output(row, GPIO.LOW)
        for j, col in enumerate(COL_PINS):
            if GPIO.input(col) == GPIO.LOW:
                GPIO.output(row, GPIO.HIGH)
                time.sleep(0.2)  # debounce
                return KEYPAD[i][j]
        GPIO.output(row, GPIO.HIGH)
    return None

def read_pin(prompt_callback=None, length=4):
    pin = ''
    if prompt_callback:
        prompt_callback('Enter PIN: ')
    while len(pin) < length:
        key = read_key()
        if key is None:
            continue
        if key == '*':
            # * clears the current input
            pin = ''
            if prompt_callback:
                prompt_callback('PIN cleared. Enter PIN: ')
            continue
        if key == '#':
            # # cancels entry
            return None
        if key.isdigit():
            pin += key
            if prompt_callback:
                prompt_callback('*' * len(pin))
    return pin
