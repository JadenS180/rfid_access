# RFID Access Control System

A two-factor door access control system built on Raspberry Pi 4. Combines RFID card authentication with keypad PIN entry, role-based access control, time-restricted permissions, and a web-based admin dashboard.

## Features

- Two-factor authentication — RFID card + 4-digit PIN required to unlock
- Role-based access control — Admin and User roles
- Time restrictions — Limit card access to specific hours of the day
- Access logging — Every attempt logged to SQLite with timestamp and reason
- Lockout protection — Cards locked out after repeated failed PIN attempts
- Web dashboard — View logs, manage users, monitor system status at port 5001
- Auto-start on boot — Both services managed via systemd

## Hardware

- Raspberry Pi 4 4GB
- RC522 RFID reader via SPI
- 4x4 membrane keypad
- Geekstory single channel relay module
- 12V solenoid lock
- Green and red LEDs with 220 ohm resistors
- Active buzzer module

## Wiring

RC522 RFID Reader
- SDA → GPIO 8
- SCK → GPIO 11
- MOSI → GPIO 10
- MISO → GPIO 9
- RST → GPIO 27
- 3.3V → 3.3V
- GND → GND

Keypad
- R1 → GPIO 12
- R2 → GPIO 16
- R3 → GPIO 20
- R4 → GPIO 21
- C1 → GPIO 18
- C2 → GPIO 23
- C3 → GPIO 24
- C4 → GPIO 25

Other Components
- Relay IN → GPIO 26
- Green LED → GPIO 19
- Red LED → GPIO 13
- Buzzer I/O → GPIO 6

## Setup

Enable SPI
    sudo raspi-config
    Interface Options → SPI → Enable → Reboot

Install dependencies
    pip3 install mfrc522 RPi.GPIO flask --break-system-packages

Enroll a card
    python3 enroll.py

Run as systemd services
    sudo systemctl enable rfid_access rfid_dashboard
    sudo systemctl start rfid_access rfid_dashboard

## Dashboard

Access at http://<pi-ip>:5001
Default admin PIN is 0000

## Project Structure

access.py       - Main access control loop
database.py     - SQLite database operations
keypad.py       - Keypad scanning logic
dashboard.py    - Flask web dashboard
config.py       - Pin assignments and settings
enroll.py       - Card enrollment utility
templates/      - HTML templates for dashboard

## Challenges

- The active buzzer turned out to be active-low, meaning it triggers on LOW instead of HIGH. Took some debugging to figure out why it was beeping constantly on startup.
- The keypad was reading keys vertically instead of horizontally. Fixed by swapping the ROW and COL pin assignments in config.py after physically testing which keys were being registered.
- The RC522 RST pin had to be moved from GPIO 25 to GPIO 27 to avoid a conflict with the keypad wiring.
- Running access.py manually while the systemd service is active causes the SPI bus to lock up entirely. Both processes try to own the RC522 and neither works. Learned this the hard way after spending a while thinking the reader had died.
- Wiring the solenoid into the relay circuit required understanding the difference between NO and NC terminals. Initially wired to NC which meant the solenoid was always powered and the lock was always open. Swapping to NO fixed it so the solenoid only triggers on access granted.
- The 12V power supply ends in a barrel jack with no exposed wires, which made connecting it to the relay screw terminals tricky. Ended up using jumper wires pushed into the barrel jack adapter to bridge into the relay terminals.

## Hardware Photos

![Full Setup](media./hardware_full.JPG)
![Half Setup](media./hardware_half.JPG)
![RC522](media./hardware_RC522.JPG)
![Keypad](media./hardware_keypad.JPG)
![Relay Module](media./hardware_relaymodule.JPG)
![Solenoid Lock](media./hardware_solenoid-lock.JPG)
![Buzzer](media./hardware_buzzer.JPG)
![Breadboard](media./hardware_breadboard.JPG)
![Pi](media./hardware_pi.JPG)

## Dashboard Screenshots

![Dashboard Main](media./dashboard1.png)
![Dashboard Users](media./dashboard_users.png)
![Dashboard Logs](media./dashboard_logs.png)
![Dashboard Denied](media./dashboard_denied.png)
![Dashboard Granted](media./dashboard_granted.png)
![Dashboard Enroll](media./dashboard_enroll.png)

## Demo

![Access Granted Demo](media./hardware_demo-success.MOV)
![Access Denied Demo](media./hardware_demo-failure.MOV)
