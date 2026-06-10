import sys
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
from database import init_db, enroll_user, get_user

def main():
    init_db()
    reader = SimpleMFRC522()

    print('=== RFID Enrollment Utility ===')
    print('Hold card near reader...')

    try:
        uid, text = reader.read()
        uid = str(uid)
        print(f'Card UID: {uid}')

        existing = get_user(uid)
        if existing:
            print(f'Card already registered to: {existing["name"]}')
            sys.exit(1)

        name = input('Enter name: ')
        pin = input('Enter 4-digit PIN: ')
        if len(pin) != 4 or not pin.isdigit():
            print('Invalid PIN. Must be exactly 4 digits.')
            sys.exit(1)

        role = input('Enter role (user/admin) [default: user]: ').strip() or 'user'
        if role not in ['user', 'admin']:
            print('Invalid role. Must be user or admin.')
            sys.exit(1)

        use_time = input('Set time restrictions? (y/n) [default: n]: ').strip().lower()
        allowed_start = None
        allowed_end = None
        if use_time == 'y':
            allowed_start = input('Allowed start time (HH:MM): ').strip()
            allowed_end = input('Allowed end time (HH:MM): ').strip()

        success = enroll_user(name, uid, pin, role, allowed_start, allowed_end)
        if success:
            print(f'Successfully enrolled {name} with role {role}')
        else:
            print('Enrollment failed. UID may already exist.')

    except KeyboardInterrupt:
        print('\nCancelled.')
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    main()
