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

rfid_access/
├── access.py        Main access control loop
├── database.py      SQLite database operations
├── keypad.py        Keypad scanning logic
├── dashboard.py     Flask web dashboard
├── config.py        Pin assignments and settings
├── enroll.py        Card enrollment utility
└── templates/       HTML templates for dashboard

## Challenges

- Active buzzer is active-low — HIGH means off, LOW means on
- Keypad ROW and COL pins had to be swapped after keypad read vertically instead of horizontally
- RC522 RST moved to GPIO 27 to avoid conflict with keypad on GPIO 25
- SPI bus conflict — only one process can own the RC522 at a time; running access.py manually while the systemd service is running causes communication failure
