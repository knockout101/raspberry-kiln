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

def print_temp():
    with temp_mutex:
        print(f'[TEMPERATURE] {CURR_TEMP} C\n')


def init_temp_sensor():
    """
    Setup function

    Setting up thread to monitor a sensor temperature

    stops double calls
    """
    global thermocouple
    global CURR_TEMP
    while True:
        with temp_mutex:
            CURR_TEMP += thermocouple.temperature
        sleep(2)


@atexit.register
def shutdown():
    print('Script Shutdown Protocol Initiated\n')
    relay_off()


##################################
##            SETUP             ##
##################################

temp_mutex = threading.Lock()

TC_MAXIMUM_TEMP_C = 1250
RELAY_SWITCH_PIN = 6
CURR_TEMP = 0

cs = digitalio.DigitalInOut(board.D5)
cs.direction = digitalio.Direction.OUTPUT

gpio.setup(RELAY_SWITCH_PIN, gpio.OUT)

SPI = board.SPI()
thermocouple = adafruit_max31856.MAX31856(SPI, cs)

t_temp = threading.Thread(target=init_temp_sensor)
t_temp.start()

##################################
##           Program            ##
##################################
answer = 0

while (answer != 4):
    answer = input("""Please Enter A Number Choice:
    1. Print Temperature
    2. Turn ON relay
    3. Turn OFF relay
    4. Exit program\n\n>> """)
    match(answer):
        case '1':
            print_temp()
        case '2':
            print_temp()
            relay_on()
        case '3':
            print_temp()
            relay_off()
        case '4':
            break
        case _:
            print("Undefined input")

print(f'[TEMPERATURE] {thermocouple.temperature} C\n')
print("System Exited Successfully!\n")
