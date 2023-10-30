
import board
import digitalio
import adafruit_max31856
import RPi.GPIO as gpio

# Showing current GPIO mode
print(f'\n[GPIO SETMODE: {gpio.getmode()}]\n')

# Setting up the actual channel to output
gpio.setup(31, gpio.IN)
print(f"\n[GPIO SETUP CHANNEL 31]\n")

# Setting output state to high = 3V
gpio.output(31, 0)
print(f"\n[GPIO OUTPUT SET TO 0!]\n")

spi = board.SPI()

cs = digitalio.DigitalInOut(board.D5)
cs.direction = digitalio.Direction.OUTPUT

thermocouple = adafruit_max31856.MAX31856(spi, cs)

print(f'[TEMPERATURE] {thermocouple.temperature} C')