import threading
import atexit
import board
import digitalio
import adafruit_max31856
import RPi.GPIO as gpio
from time import sleep, time

# Schedules
bisque_schedule = {
                    "predry_heating" : [0, 200],
                    "initial_heating": [(200,1000), 250, 250/60],
                    "medium_heating": [(1000, 1500), 200, 200/60],
                    "final_heating": [(1500, 1850), 150, 150/60],
                    "soaking": [1850, 20]
                }
# States
relay_state = False # starts off
    # Reperesents state of completion
SOAKING = False
# Mutexes
temp_mutex = threading.Lock()
hour_mutex = threading.Lock()
min_mutex = threading.Lock()
# Constants
TC_MAXIMUM_TEMP_C = 1250
RELAY_SWITCH_PIN = 6
ONE_HOUR_IN_S = 3600


ONE_MIN_IN_S = 60
# Current temperature
CURR_TEMP = 0
# Calculated Rates
HOUR_RATE = 0
MIN_RATE = 0
# Setup chip select pin for breakout board
cs = digitalio.DigitalInOut(board.D5)
cs.direction = digitalio.Direction.OUTPUT
# GPIO setup relay pin to output
gpio.setup(RELAY_SWITCH_PIN, gpio.OUT)
# Thermocouple SPIBUS setup and object initialized
SPI = board.SPI()
thermocouple = adafruit_max31856.MAX31856(SPI, cs)
# Time delay for watchdog thread to poll TC
SENSOR_DELAY = 1
# Actual Temperature
TEST_TEMPERATURE = 90
# Temperature trimmed by 15 to address the thermal profile and position of the TC 
TRIMMED_TEMPERATURE = TEST_TEMPERATURE - 15



def hour_check()                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
    global CURR_TEMP
    global HOUR_RATE
    while 1:
        starting_time = time()
        with temp_mutex:
            starting_temp = CURR_TEMP
        # Sleep for one hour
        sleep(ONE_HOUR_IN_S)
        time_passed = time() - starting_time
        with temp_mutex:
            temp_diff = CURR_TEMP - starting_temp

        with hour_mutex:
            HOUR_RATE = temp_diff / time_passed


def min_check():
    global CURR_TEMP
    global MIN_RATE
    while 1:
        starting_time = time()
        with temp_mutex:
            starting_temp = CURR_TEMP
        # Sleep for 1 minute
        sleep(ONE_MIN_IN_S)
        time_passed = time() - starting_time
        with temp_mutex:
            temp_diff = CURR_TEMP - starting_temp

        with min_mutex:
            MIN_RATE = temp_diff / time_passed


def pull_min_rate() -> int:
    """Obtaining mutex and polling last known per minute heating rate in IPC variable MIN_RATE"""
    with min_mutex:
        rate_now = MIN_RATE
    return rate_now


def pull_hour_rate() -> int:
    """Obtaining mutex and polling last known hourly heating rate in IPC variable HOUR_RATE"""
    with hour_mutex:
        rate_now = HOUR_RATE
    return rate_now


def pull_temp() -> int:
    """Polling last known temperature in the IPC variable CURR_TEMP and returning it"""
    with temp_mutex:
        res = CURR_TEMP
    return res


def min_rate_delay() -> None:
    relay_off()
    sleep(10)
    relay_on()
 

def hour_rate_delay() -> None:
    relay_off()
    sleep(30)
    relay_on()


def hold_temp(temperature: int, duration: int) -> None:
    starting_time = time()
    while True:
        temp = pull_temp
        print(f"Current temperature = {temp}")
        if temp < temperature:
            relay_on()
        else:
            relay_off()
        time_diff = time() - starting_time
        if time_diff > duration:
            return
        sleep(SENSOR_DELAY)


def start_schedule() -> None:
    # Start threads
    t_hour_check.start()
    t_min_check.start()
    # Turn on relay to start heating
    relay_on()
    # Record starting time
    starting_time = time()
    while 1:
        temp_now = pull_temp()
        match temp_now:
            case x if x > bisque_schedule["predry_heating"][0] and x <= bisque_schedule["predry_heating"][1]:
                pass
            case x if x > bisque_schedule["initial_heating"][0][0] and x <= bisque_schedule["initial_heating"][0][1]:
                if pull_min_rate > bisque_schedule["initial_heating"][2]:
                    min_rate_delay()
                if pull_hour_rate > bisque_schedule["initial_heating"][2]:
                    hour_rate_delay() 
            case x if x > bisque_schedule["medium_heating"][0][0] and x <= bisque_schedule["medium_heating"][0][1]:
                if pull_min_rate > bisque_schedule["medium_heating"][2]:
                    min_rate_delay()
                if pull_hour_rate > bisque_schedule["medium_heating"][2]:
                    hour_rate_delay()
            case x if x > bisque_schedule["final_heating"][0][0] and x <= bisque_schedule["final_heating"][0][1]:
                if pull_min_rate > bisque_schedule["final_heating"][2]:
                    min_rate_delay()
                if pull_hour_rate > bisque_schedule["final_heating"][2]:
                    hour_rate_delay()
            case x if x > bisque_schedule["soaking"][0] and SOAKING == 0:
                hold_temp(bisque_schedule["soaking"][0])
                SOAKING = True # show completed
            case 0:
                raise ZeroReadingError("Reading 0 from thermocouple")
            case _:
                raise OutOfBoundsError("[FAULT] - CURR_TEMP is out of bounds")
        
        sleep(60)


class ZeroReadingError(Exception):
    """Raised when the TC is sending a 0 degree reading"""
    pass


class OutOfBoundsError(Exception):
    """Raised when the TC is sending a reading out of the bounds of all other cases (default)"""
    pass


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


if __name__ == "__main__":
    answer = 0
    t_temp = threading.Thread(target=init_temp_sensor)
    t_hour_check = threading.Thread(target=hour_check)
    t_min_check = threading.Thread(target=min_check)
    t_temp.start()

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
                try:    
                    start_schedule()
                except (ZeroReadingError, OutOfBoundsError) as e:
                    print("[SCHEDULE ERROR] - {e}")
                    break
            case '5':
                break
            case _:
                print("Undefined input")

    print(f'[TEMPERATURE] {thermocouple.temperature} C\n')
    print("System Exited Successfully!\n")
