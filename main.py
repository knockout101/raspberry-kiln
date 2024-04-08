import threading
import atexit
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


def print_temp():
    print('\n')
    print(f'[TEMPERATURE] {temp} C\n')


def init_temp_sensor():
    """
    Setup function

    Setting up thread to monitor a sensor temperature

    stops double calls
    """
    SPI = board.SPI()

    thermocouple = adafruit_max31856.MAX31856(SPI, cs)

    if temp1.running:
        raise (threading.ThreadError("sensor is already running"))
    temp1 = threading.Thread(target=init_temp_sensor, daemon=True)
    temp1.start()
    print("[Temperature Sensor] Initiated\n")
    while True:
        global temp = thermocouple.temperature


@atexit.register
def shutdown():
    print('Script Shutdown Protocol Initiated\n')
    relay_off()


##################################
##            SETUP             ##
##################################


RELAY_SWITCH_PIN = 6


cs = digitalio.DigitalInOut(board.D5)
cs.direction = digitalio.Direction.OUTPUT

gpio.setup(RELAY_SWITCH_PIN, gpio.OUT)

temp = 0
answer = 0

init_temp_sensor()

##################################
##           Program            ##
##################################


while (answer != 4):
    answer = input("""Please Enter A Number Choice:
    1. Print Temperature
    2. Turn ON relay
    3. Turn OFF relay
    4. Exit program\n\n>> """)
    match(answer):
        case '1':
            print_temp()
            break
        case '2':
            print_temp()
            relay_on()
            break
        case '3':
            print_temp()
            relay_off()
            break
        case '4':
            break
        case _:
            print("Undefined input")

print(f'[TEMPERATURE] {thermocouple.temperature} C\n')
print("System Exited Successfully!\n")
