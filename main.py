
import board
import digitalio
import adafruit_max31856
import RPi.GPIO as gpio
from time import sleep


def relay_off():
    print(f"{'='*20} \n Relay turned OFF \n {'='*20} \n")
    gpio.output(RELAY_SWITCH_PIN, gpio.LOW)

def relay_on():
    print(f"{'='*20} \n Relay turned ON \n {'='*20} \n")
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
while(answer != 4):
    answer = input("""Please Enter A Number Choice:
    1. Print Temperature
    2. Turn ON relay
    3. Turn OFF relay
    4. Exit program\n\n>> """)
    match(answer):
        case '1':
            print(f'[TEMPERATURE] {thermocouple.temperature} C\n')
        case '2':
            relay_on()
        case '3':
            relay_off()
        case '4':
            break
        case _:
            print("Undefined input")

    print(f'[TEMPERATURE] {thermocouple.temperature} C\n')

