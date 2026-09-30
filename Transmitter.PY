import smbus2 
import time 
import datetime 
from lora import LoRa 
import RPi.GPIO as GPIO 
import json 
import threading 
 
# I2C addresses 
PCF8591_ADDRESS = 0x48 
GY87_ADDRESS = 0x68 
 
# Initialize I2C 
bus = smbus2.SMBus(1) 
 
# GPIO setup (for LoRa DIO0 pin) 
GPIO.setmode(GPIO.BCM) 
DIO0_PIN = 17 
GPIO.setup(DIO0_PIN, GPIO.IN) 
 
 
# Function to read from PCF8591 ADC 
def read_adc(channel): 
    try: 
        bus.write_byte(PCF8591_ADDRESS, channel) 
        return bus.read_byte(PCF8591_ADDRESS)
         except Exception as e: 
        print(f"Error reading ADC channel {channel}: {e}") 
        return None 
 
 
# Function to initialize the GY-87 sensor 
def init_gy87(): 
    try: 
        bus.write_byte_data(GY87_ADDRESS, 0x6B, 0x00)  # Wake up MPU6050 
    except Exception as e: 
        print(f"Error initializing GY-87: {e}") 
 
 
# Function to read from GY-87 sensor 
def read_gy87(): 
    try: 
        accel_x = bus.read_byte_data(GY87_ADDRESS, 0x3B) 
        accel_y = bus.read_byte_data(GY87_ADDRESS, 0x3D) 
        accel_z = bus.read_byte_data(GY87_ADDRESS, 0x3F) 
        return accel_x, accel_y, accel_z 
    except Exception as e: 
        print(f"Error reading GY-87: {e}") 
        return None, None, None
        # Function to initialize LoRa module 
def init_lora(): 
    try: 
        lora = LoRa(mode=LoRa.LORA, region=LoRa.EU868, frequency=868.0, 
pins={'dio0': DIO0_PIN}) 
        lora.set_tx_power(14) 
        return lora 
    except Exception as e: 
        print(f"Error initializing LoRa: {e}") 
        return None 
 
 
# Function to get current time in the required format 
def get_current_time(): 
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
 
 
# Function to log data locally 
def log_data(data): 
    with open("data_log.json", "a") as log_file: 
        json.dump(data, log_file) 
        log_file.write('\n') 
         
# Function to collect sensor data 
def collect_data(): 
    init_gy87() 
    lora = init_lora() 
 
    if not lora: 
        print("LoRa initialization failed. Exiting...") 
        return 
        pzt1_value = read_adc(0x00) 
        pzt2_value = read_adc(0x01) 
        pzt3_value = read_adc(0x02) 
        pzt4_value = read_adc(0x03) 
 
        accel_x, accel_y, accel_z = read_gy87() 
        if None in (accel_x, accel_y, accel_z): 
            continue 
 
        vibration = (accel_x  2 + accel_y  2 + accel_z  2)  0.5 
 
        data = { 
            'time': current_time, 
            'PZT1': pzt1_value, 
            'PZT2': pzt2_value, 
            'PZT3': pzt3_value, 
            'PZT4': pzt4_value, 
            'vibration': round(vibration, 2) 
        } 
 
        try: 
            lora.send(json.dumps(data)) 
        except Exception as e: 
            print(f"Error sending data via LoRa: {e}")
 
    while True: 
        current_time = get_current_time()
         log_data(data) 
 
        print(data) 
        time.sleep(1) 
 
 
if __name__ == "__main__": 
    data_thread = threading.Thread(target=collect_data) 
    data_thread.start()
