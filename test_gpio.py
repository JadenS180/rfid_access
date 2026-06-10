import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

RELAY_PIN = 26
GREEN_LED_PIN = 19
RED_LED_PIN = 13
BUZZER_PIN = 6

pins = [RELAY_PIN, GREEN_LED_PIN, RED_LED_PIN, BUZZER_PIN]

for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# Active low buzzer needs to start HIGH (off)
GPIO.output(BUZZER_PIN, GPIO.HIGH)

print("Testing GREEN LED...")
GPIO.output(GREEN_LED_PIN, GPIO.HIGH)
time.sleep(2)
GPIO.output(GREEN_LED_PIN, GPIO.LOW)

print("Testing RED LED...")
GPIO.output(RED_LED_PIN, GPIO.HIGH)
time.sleep(2)
GPIO.output(RED_LED_PIN, GPIO.LOW)

print("Testing BUZZER...")
GPIO.output(BUZZER_PIN, GPIO.LOW)
time.sleep(1)
GPIO.output(BUZZER_PIN, GPIO.HIGH)

print("Testing RELAY...")
GPIO.output(RELAY_PIN, GPIO.HIGH)
time.sleep(2)
GPIO.output(RELAY_PIN, GPIO.LOW)

print("All done.")
GPIO.cleanup()
