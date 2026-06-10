import RPi.GPIO as GPIO
import time
import sys
from datetime import datetime
from config import (
    RELAY_PIN, GREEN_LED_PIN, RED_LED_PIN, BUZZER_PIN,
    RELAY_UNLOCK_TIME, MAX_FAILED_ATTEMPTS, LOCKOUT_DURATION, PIN_LENGTH
)
from database import (
    init_db, get_user, verify_pin, log_access,
    log_failed_attempt, get_recent_failed_attempts
)
from keypad import init_keypad, read_pin
from mfrc522 import SimpleMFRC522
import warnings
warnings.filterwarnings('ignore')

def init_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(RELAY_PIN, GPIO.OUT)
    GPIO.setup(GREEN_LED_PIN, GPIO.OUT)
    GPIO.setup(RED_LED_PIN, GPIO.OUT)
    GPIO.setup(BUZZER_PIN, GPIO.OUT)
    GPIO.output(RELAY_PIN, GPIO.LOW)
    GPIO.output(GREEN_LED_PIN, GPIO.LOW)
    GPIO.output(RED_LED_PIN, GPIO.LOW)
    GPIO.output(BUZZER_PIN, GPIO.HIGH)

def unlock():
    GPIO.output(RELAY_PIN, GPIO.HIGH)
    GPIO.output(GREEN_LED_PIN, GPIO.HIGH)
    beep(0.1)
    time.sleep(RELAY_UNLOCK_TIME)
    GPIO.output(RELAY_PIN, GPIO.LOW)
    GPIO.output(GREEN_LED_PIN, GPIO.LOW)

def deny():
    GPIO.output(RED_LED_PIN, GPIO.HIGH)
    beep(0.5)
    time.sleep(1)
    GPIO.output(RED_LED_PIN, GPIO.LOW)

def beep(duration):
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    time.sleep(duration)
    GPIO.output(BUZZER_PIN, GPIO.HIGH)

def check_time_restrictions(user):
    if user['allowed_start'] is None or user['allowed_end'] is None:
        return True
    now = datetime.now().strftime('%H:%M')
    return user['allowed_start'] <= now <= user['allowed_end']

def is_locked_out(uid):
    failed = get_recent_failed_attempts(uid, LOCKOUT_DURATION)
    return failed >= MAX_FAILED_ATTEMPTS

def main():
    init_db()
    init_gpio()
    init_keypad()
    reader = SimpleMFRC522()

    print('RFID Access Control System Running...')
    print('Waiting for card...')

    try:
        while True:
            # Step 1: Read RFID card
            uid, text = reader.read()
            uid = str(uid)
            print(f'Card detected: {uid}')

            # Step 2: Check lockout
            if is_locked_out(uid):
                print('Card is locked out due to failed attempts')
                log_access(uid, None, 'DENIED', 'Locked out')
                deny()
                time.sleep(2)
                continue

            # Step 3: Look up user
            user = get_user(uid)
            if user is None:
                print('Unknown card')
                log_access(uid, None, 'DENIED', 'Unknown card')
                deny()
                time.sleep(2)
                continue

            # Step 4: Check time restrictions
            if not check_time_restrictions(user):
                print(f'Access denied for {user["name"]} - outside allowed hours')
                log_access(uid, user['name'], 'DENIED', 'Outside allowed hours')
                deny()
                time.sleep(2)
                continue

            # Step 5: Read PIN
            print(f'Card recognized: {user["name"]}. Enter PIN.')
            beep(0.1)
            time.sleep(0.3)
            beep(0.1)
            pin = read_pin(length=PIN_LENGTH)

            if pin is None:
                print('PIN entry cancelled')
                time.sleep(1)
                continue

            # Step 6: Verify PIN
            if not verify_pin(user, pin):
                print('Incorrect PIN')
                log_failed_attempt(uid)
                log_access(uid, user['name'], 'DENIED', 'Wrong PIN')
                deny()
                time.sleep(2)
                continue

            # Step 7: Grant access
            print(f'Access granted for {user["name"]}')
            log_access(uid, user['name'], 'GRANTED', None)
            unlock()

            print('Waiting for next card...')
            time.sleep(1)

    except KeyboardInterrupt:
        print('Shutting down...')
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    main()
