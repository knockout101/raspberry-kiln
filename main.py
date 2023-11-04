
import board
import digitalio
import adafruit_max31856
import RPi.GPIO as gpio
from time import sleep

RELAY_SWITCH_PIN = 6

SPI = board.SPI()

# On/Off functions for relay
def relay_off():
    print("Relay turned OFF")
    gpio.output(RELAY_SWITCH_PIN, gpio.LOW)

def relay_on():
    print("Relay turned ON \n =*20")
    gpio.output(RELAY_SWITCH_PIN, gpio.HIGH)

def relay_blink(delay, blinks):
    for _ in range(blinks):
        relay_on()
        sleep(delay)
        relay_off()
        sleep(delay)

# Setting up GPIO06 Output
gpio.setup(6, gpio.OUT)

gpio.out(RELAY_SWITCH_PIN, gpio.LOW)

relay_blink(200, 10)

print("\n[DIGITALIO PIN D6 SET TO OUTPUT]\n")

cs = digitalio.DigitalInOut(board.D5)
cs.direction = digitalio.Direction.OUTPUT

thermocouple = adafruit_max31856.MAX31856(SPI, cs)

print(f'[TEMPERATURE] {thermocouple.temperature} C')

