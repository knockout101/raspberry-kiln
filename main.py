
import board
import digitalio
import adafruit_max31856
import RPi.GPIO as gpio
from time import sleep


def relay_off():
    print("Relay turned OFF")
    gpio.output(RELAY_SWITCH_PIN, gpio.LOW)

def relay_on():
    print(f"Relay turned ON \n {'='*20}")
    gpio.output(RELAY_SWITCH_PIN, gpio.HIGH)

def relay_blink(delay, blinks):
    for _ in range(blinks):
        relay_on()
        sleep(delay)
        relay_off()
        sleep(delay)


##################################
##            SETUP             ##
##################################

RELAY_SWITCH_PIN = 6

SPI = board.SPI()

cs = digitalio.DigitalInOut(board.D5)
cs.direction = digitalio.Direction.OUTPUT
thermocouple = adafruit_max31856.MAX31856(SPI, cs)

gpio.setup(RELAY_SWITCH_PIN, gpio.OUT)

answer = 0
while(answer != 3):
    answer = input("""Please Enter A Number Choice:
1. turn on relay
2. turn off relay
3. exit program\n>>""")
    match(answer):
        case '1':
            relay_on()
            print("[RELAY SWITCH] >> ON <<")
        case '2':
            relay_off()
            print("[RELAY SWITCH] OFF")
        case '3':
            exit(0)
        case default:
            print("Undefined input")

    print(f'[TEMPERATURE] {thermocouple.temperature} C')

