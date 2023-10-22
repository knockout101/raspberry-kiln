import board
import digitalio
import adafruit_max31856
import RPi.GPIO as gpio

# Showing current GPIO mode
print(f'\n[GPIO SETMODE: {gpio.getmode()}]\n')

# Setting up the actual channel to output
gpio.setup(31, gpio.OUT)
print(f"\n[GPIO SETUP CHANNEL 31]\n")

# Setting output state to high = 3V
gpio.output(31, gpio.HIGH)
print(f"\n[GPIO OUTPUT STATE HIGH SET TO CHANNEL 31]\n")

spi = board.SPI()

cs = digitalio.DigitalInOut(board.D5)
cs.direction = digitalio.Direction.OUTPUT

thermocouple = adafruit_max31856.MAX31856(spi, cs)

print(thermocouple.temperature)