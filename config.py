# GPIO Pin Configuration
RELAY_PIN = 26
RC522_RST_PIN = 22
GREEN_LED_PIN = 19
RED_LED_PIN = 13
BUZZER_PIN = 6

# Keypad GPIO pins
COL_PINS = [18, 23, 24, 25]
ROW_PINS = [12, 16, 20, 21]

# Keypad layout
KEYPAD = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

# Access settings
RELAY_UNLOCK_TIME = 3        # seconds the relay stays open
MAX_FAILED_ATTEMPTS = 3      # failed attempts before lockout
LOCKOUT_DURATION = 60        # lockout duration in seconds
PIN_LENGTH = 4               # required PIN length

# Database
DB_PATH = '/home/jaden/rfid_access/access.db'

# Dashboard
DASHBOARD_PORT = 5001
DASHBOARD_HOST = '0.0.0.0'

# Admin default PIN (change after first login)
ADMIN_DEFAULT_PIN = '0000'
