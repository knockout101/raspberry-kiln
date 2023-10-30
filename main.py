
import board
import digitalio
import adafruit_max31856
import RPi.GPIO as gpio
from time import sleep

# Showing current GPIO mode
print(f'\n[GPIO SETMODE: {gpio.getmode()}]\n')

# Setting up the actual channel to output
gpio.setup(6, gpio.OUT)

gpio.output(6, gpio.HIGH)

print("\n[DIGITALIO PIN D6 SET TO OUTPUT]\n")

# Setting output state to high = 3V
# gpio.input(31, 0)
# print(f"\n[GPIO OUTPUT SET TO 0!]\n")

spi = board.SPI()

cs = digitalio.DigitalInOut(board.D5)
cs.direction = digitalio.Direction.OUTPUT

thermocouple = adafruit_max31856.MAX31856(spi, cs)

print(f'[TEMPERATURE] {thermocouple.temperature} C')

input("Press any key to cleanup and exit the program.")
