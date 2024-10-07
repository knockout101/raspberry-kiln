import threading
import atexit
import board
import digitalio
import adafruit_max31856
import RPi.GPIO as gpio
from time import sleep, time
"""
MAX31856 units out - Celsius
"""
# Schedules:
# predry and soaking stages only have heat ranges ( [0], [1] ]
# indexing
#   [0] - heat range (min , max]
#   [1] - maximum heat increase per hour in F
#   [2] - maximum heat increase per minute in F
bisque_schedule = {
                    "predry_heating" : [0, 100],
                    "initial_heating": [(100,120), 139, 139/60],
                    "final_heating": [(650, 1000), 167, 167/60],
                    "soaking": [1000, 30]
                }
# States
relay_state = False # starts off
# Mutexes
temp_mutex = threading.Lock()
hour_mutex = threading.Lock()
min_mutex = threading.Lock()
# Constants
SOAKING_DURATION = 30*60  # in seconds
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
# Data file constant
DATA_FILE = "data.csv"



def hour_check():                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
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
    sleep(30)
    relay_on()
 

def hour_rate_delay() -> None:
    relay_off()
    sleep(10*60) # 10 minutes (10 * 60 seconds)
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
        if time_diff >= duration:
            return
        sleep(SENSOR_DELAY)

def save_temp(curr_temp: float, time_marker: float):
    with open(DATA_FILE, "w+") as data_file:
        data_file.write(f"{curr_temp},{time_marker}")


def start_bisque_schedule() -> None:
    # Start threads
    state = "initializing"
    t_hour_check.start()
    t_min_check.start()
    # Turn on relay to start heating
    relay_on()
    # Record starting time
    starting_time = time()
    while 1:
        # Pull current temp from shared variable
        temp_now = pull_temp()
        # save temperature data
        save_temp(temp_now, time() - starting_time)
        match temp_now:
            # Pre-heating stage, no maximum heating rate, pass when x is in predry_heating range
            case x if x > bisque_schedule["predry_heating"][0] and x <= bisque_schedule["predry_heating"][1]:
                if state != "predry":
                    state = "predry"
                pass
            # Initial-heating stage, maximum heating per hour and minute, if current calculated rate is greater than
            # maximum rates, appropriate delays input to slow heating respectively. Check and assign appropriate state 
            # Note: for initial stage index 0 is a tuple (min, max)
            case x if x > bisque_schedule["initial_heating"][0][0] and x <= bisque_schedule["initial_heating"][0][1]:
                if state != "initial":
                    state = "initial"
                # Indexing note: [1] is hourly rate and [2] is the minutely rate
                if pull_min_rate() > bisque_schedule["initial_heating"][2]:
                    min_rate_delay()
                if pull_hour_rate() > bisque_schedule["initial_heating"][1]:
                    hour_rate_delay() 
            # Final-heating state, maximum heating per hour and minute, if current calculated rate is greater than 
            # maximum rates, delay appropriately, check and assign appropriate state
            # Note: for final stage index 0 is a tuple (min, max)
            case x if x > bisque_schedule["final_heating"][0][0] and x <= bisque_schedule["final_heating"][0][1]:
                if state != "final":
                    state = "final"
                # Indexing note: [1] is hourly rate and [2] is the minutely rate
                if pull_min_rate() > bisque_schedule["final_heating"][2]:
                    min_rate_delay()
                if pull_hour_rate() > bisque_schedule["final_heating"][1]:
                    hour_rate_delay()
            # When soaking temperature is reached hold temperature for 
            case x if x > bisque_schedule["soaking"][0]:
                if state != "soaking":
                    state = "soaking"
                # Duration is set to seconds for - 30 minutes
                hold_temp(bisque_schedule["soaking"][0], SOAKING_DURATION)
                # Print schedule duration in hours
                duration = time() - starting_time
                print(f"Schedule lasted: {duration / ONE_HOUR_IN_S}")
                # Schedule is completed
                return
            # Zero reading means the probe is broken or the wiring is disconnect, throw error    
            case 0:
                raise ZeroReadingError("Reading 0 from thermocouple")
            # Any values read outside of range specified and not zero throw error, expected real bounds in celsius [23, 1000]
            case _:
                raise OutOfBoundsError("[FAULT] - CURR_TEMP is out of bounds")
        # delay 30 seconds for checking minutely rate at 2:1 not just 1:1 on timing
        sleep(30)


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
    global CURR_TEMP
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
                print("Initialize bisque fire schedule")
                try:
                    start_bisque_schedule()
                except (ZeroReadingError, OutOfBoundsError) as e:
                    print("[SCHEDULE ERROR] - {e}")
                    relay_off()
                    break
            case '5':
                break
            case _:
                print("Undefined input")

    print(f'[TEMPERATURE] {thermocouple.temperature} C\n')
    print("System Exited Successfully!\n")
