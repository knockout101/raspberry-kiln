import threading
import atexit
import board
import digitalio
import adafruit_max31856
import RPi.GPIO as gpio
from time import sleep, time

bisque_schedule = {
                    initial_heating: [(200,1000), 250],
                    medium_heating: [(1000, 1500), 200],
                    final_heating: [(1500, 1850), 150],
                    soaking: [1850, 20]
                }

def start_schedule()
    global CURR_TEMP

# Time delay for watchdog thread to poll TC
SENSOR_DELAY = 1
# Actual Temperature
TEST_TEMPERATURE = 90
# Temperature trimmed by 15 to address the thermal profile and position of the TC 
TRIMMED_TEMPERATURE = TEST_TEMPERATURE - 15

def low_temp_test_schedule():
    "Test the kiln to maintain test temperature"
    global relay_state
    while(True):
        with temp_mutex:
            temp = CURR_TEMP
            print(f"Current temperature = {temp}")
        if(temp < TRIMMED_TEMPERATURE):
            relay_on()
        else:
            relay_off()
        sleep(SENSOR_DELAY)


def relay_off():
    """
    Switches relay off, sets state to false, and prints a log message
    
    Relay state is checked before code block is executed, stopping unnecessary code execution
    """
    global relay_state
    if not relay_state: # return if relay is already off
        return
    print(f"{'='*20} \n Relay turned OFF \n {'='*20} \n")
    gpio.output(RELAY_SWITCH_PIN, gpio.LOW)
    relay_state = False


def relay_on():
    """
    Switches relay on, sets state to true, and prints a log message
    
    Relay state is checked before code block is executed, stopping unnecessary code execution
    """
    global relay_state
    if relay_state: # return if relay is already on
        return
    print(f"{'='*20} \n Relay turned ON \n {'='*20} \n")
    gpio.output(RELAY_SWITCH_PIN, gpio.HIGH)
    relay_state = True


def print_temp():
    """Obtains the mutex for temperature sensor"""
    with temp_mutex:
        print(f'[TEMPERATURE] {CURR_TEMP} C\n')


def init_temp_sensor():
    """
    Setup function

    Setting up thread to monitor a sensor temperature

    stops double calls
    """
    global thermocouple
    while True:
        with temp_mutex:
            CURR_TEMP = thermocouple.temperature
        sleep(SENSOR_DELAY)


@atexit.register
def shutdown():
    """When system is shutdown relay is always turned off"""
    print('Script Shutdown Protocol Initiated\n')
    relay_off()


##################################
##            SETUP             ##
##################################

relay_state = False # starts off

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
    4. Test Schedule @ 90 Celsius
    5. Exit program\n\n>> """)
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
            print("Initiating test at 90 Celsius")
            low_temp_test_schedule()
        case '5':
            break
        case _:
            print("Undefined input")

print(f'[TEMPERATURE] {thermocouple.temperature} C\n')
print("System Exited Successfully!\n")
