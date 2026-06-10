import RPi.GPIO as GPIO
from keypad import init_keypad, read_key

init_keypad()
print('Press keys on keypad (Ctrl+C to quit):')
try:
    while True:
        key = read_key()
        if key:
            print(f'Key pressed: {key}')
except KeyboardInterrupt:
    print('Done')
finally:
    GPIO.cleanup()
