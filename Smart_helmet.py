from machine import Pin, I2C, ADC, time_pulse_us, SoftI2C
import ssd1306
from time import sleep
import time
import math
import network
import mrequests
import socket
# Global variables
digital_value = 0
total_accel = 0
gyro_x, gyro_y, gyro_z = 0, 0, 0
fsr_value = 0
vibration_value = 0
distance = 0

ACCEL_THRESHOLD = 3.0  
GYRO_THRESHOLD = 180.0

# I2C for MPU6050
i2c_mpu = I2C(0, scl=Pin(22), sda=Pin(21))  # Hardware I2C

# I2C for OLED
i2c_oled = SoftI2C(scl=Pin(25), sda=Pin(26))
oled_width, oled_height = 128, 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c_oled)

# Wi-Fi credentials
SSID = "Archismans23fe"
PASSWORD = "archisman2004"
# Server IP and port
SERVER_IP = "192.168.76.162"  # Replace with the server's IP address
SERVER_PORT = 80

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    print("Connecting to Wi-Fi...")
    while not wlan.isconnected():
        pass
    print("Connected to Wi-Fi!")
    print(wlan.ifconfig())

# Blynk credentials
BLYNK_TOKEN = "AnOPZqT7enN6fdXKwyJ5aCfZF6_w6hzc"
EVENT_CODE1 = "smart_helmet"
url1 = f"http://blynk.cloud/external/api/logEvent?token={BLYNK_TOKEN}&code={EVENT_CODE1}"
EVENT_CODE2="alcohol_detected"
url2 = f"http://blynk.cloud/external/api/logEvent?token={BLYNK_TOKEN}&code={EVENT_CODE2}"
def trigger_event():
    try:
        response = mrequests.get(url1)
        print("Response Code:", response.status_code)
        print("Response Text:", response.text)
        response.close()
    except Exception as e:
        print("Error while sending request:", e)
def trigger_warning():
    try:
        response = mrequests.get(url2)
        print("Response Code:", response.status_code)
        print("Response Text:", response.text)
        response.close()
    except Exception as e:
        print("Error while sending request:", e)
    def trigger_event_with_retry(retries=3):
    for attempt in ranger(,,retries):
        try:
            trigger_event()
            break  # Exit loop if successful
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2)
    else:
        print("All attempts to trigger event failed.")

def send_trigger(trigger_type):
    """
    Sends a trigger message to the server.
    trigger_type: str ("TRIGGER1" to turn ON, "TRIGGER2" to turn OFF)
    """
    addr = socket.getaddrinfo(SERVER_IP, SERVER_PORT)[0][-1]
    client = socket.socket()
    client.connect(addr)
    print("Connected to server:", addr)
  
    request = "GET /{} HTTP/1.1\r\nHost: {}\r\n\r\n".format(trigger_type, SERVER_IP)
    client.send(request.encode("utf-8"))
    print(f"{trigger_type} message sent!")
    
    response = client.recv(1024).decode("utf-8")
    print("Response from server:", response)
    client.close()
# MQ3 Alcohol Detection
def alcohol():
    global digital_value
    mq3_digital_pin = Pin(15, Pin.IN)  # GPIO15 as input
    digital_value = mq3_digital_pin.value()
    return digital_value

# MPU6050 Crash Detection
def gyroscope_accelerometer():
    global total_accel, gyro_x, gyro_y, gyro_z
    MPU6050_ADDR = 0x68
    PWR_MGMT_1 = 0x6B
    ACCEL_XOUT_H = 0x3B
    GYRO_XOUT_H = 0x43

    def init_mpu6050():
        i2c_mpu.writeto_mem(MPU6050_ADDR, PWR_MGMT_1, b'\x00')  # Wake up MPU6050

    def read_word(register):
        high, low = i2c_mpu.readfrom_mem(MPU6050_ADDR, register, 2)
        value = (high << 8) | low
        return value - 65536 if value > 32767 else value

    def read_acceleration():
        ax = read_word(ACCEL_XOUT_H) / 16384.0
        ay = read_word(ACCEL_XOUT_H + 2) / 16384.0
        az = read_word(ACCEL_XOUT_H + 4) / 16384.0
        return ax, ay, az

    def read_gyroscope():
        gx = read_word(GYRO_XOUT_H) / 131.0
        gy = read_word(GYRO_XOUT_H + 2) / 131.0
        gz = read_word(GYRO_XOUT_H + 4) / 131.0
        return gx, gy, gz

    init_mpu6050()
    accel_x, accel_y, accel_z = read_acceleration()
    gyro_x, gyro_y, gyro_z = read_gyroscope()
    total_accel = math.sqrt(accel_x*2 + accel_y2 + accel_z*2)

# FSR Sensor Detection
def read_fsr():
    global fsr_value,fsr_value1
    fsr_pin = ADC(Pin(36))
    fsr_pin1 = ADC(Pin(34))
    fsr_pin.atten(ADC.ATTN_11DB)
    fsr_pin1.atten(ADC.ATTN_11DB)
    fsr_value = fsr_pin.read()
    fsr_value1 = fsr_pin1.read()
    return fsr_value
    return fsr_value1

# Vibration Sensor Detection
def read_analog_vibration():
    global vibration_value
    vibration_pin = ADC(Pin(33))
    vibration_pin.atten(ADC.ATTN_11DB)
    vibration_value = vibration_pin.read()
    if vibration_value > 3000:
        print("Strong vibration detected!")
    elif vibration_value > 1000:
        print("Mild vibration detected!")
def ultrasonic():
    TRIG_PIN = 5
    ECHO_PIN = 18
    TRIG_PIN_LEFT = 2
    ECHO_PIN_LEFT = 4
    TRIG_PIN_RIGHT = 13
    ECHO_PIN_RIGHT = 12

    trigleft = Pin(TRIG_PIN_LEFT, Pin.OUT)
    echoleft = Pin(ECHO_PIN_LEFT, Pin.IN)
    trigright = Pin(TRIG_PIN_RIGHT, Pin.OUT)
    echoright = Pin(ECHO_PIN_RIGHT, Pin.IN)
    trig = Pin(TRIG_PIN, Pin.OUT)
    echo = Pin(ECHO_PIN, Pin.IN)

    global distance, distanceleft, distanceright

    def measure_distanceleft():
        trigleft.value(0)
        time.sleep_us(2)
        trigleft.value(1)
        time.sleep_us(10)
        trigleft.value(0)
        pulse_time = time_pulse_us(echoleft, 1, 50000)
        if pulse_time < 0:
            return None
        return (pulse_time / 2) / 29.1

    def measure_distanceright():
        trigright.value(0)
        time.sleep_us(2)
        trigright.value(1)
        time.sleep_us(10)
        trigright.value(0)
        pulse_time = time_pulse_us(echoright, 1, 50000)
        if pulse_time < 0:
            return None
        return (pulse_time / 2) / 29.1

    def measure_distance():
        trig.value(0)
        time.sleep_us(2)
        trig.value(1)
        time.sleep_us(10)
        trig.value(0)
        pulse_time = time_pulse_us(echo, 1, 50000)
        if pulse_time < 0:
            return None
        return (pulse_time / 2) / 29.1

    # Measure distances
    distanceleft = measure_distanceleft()
    time.sleep(0.1)
    distanceright = measure_distanceright()
    time.sleep(0.1)
    distance = measure_distance()

    


# Main Loop
receiver_name = "ESP32_Receiver" 
connect_wifi()

while True:
    try:
        alcohol()
        read_fsr()
        gyroscope_accelerometer()
        read_analog_vibration()
        ultrasonic()
        time.sleep(0.3)

        oled.fill(0)  # Clear the screen
        if fsr_value == 4095:
            oled.text('Helmet Worn', 0, 0)
            oled.show()
            send_trigger_with_retry("TRIGGER1")
            print("Helmet worn")
            if digital_value == 0:
                oled.text('Bike Won\'t Start!', 0, 20)
                oled.text('Alcohol Detected!', 0, 30)
                oled.show()
                send_trigger_with_retry("TRIGGER2")
                trigger_warning_with_retry()
            # Crash detection logic
            if (total_accel > ACCEL_THRESHOLD or
                abs(gyro_x) > GYRO_THRESHOLD or
                abs(gyro_y) > GYRO_THRESHOLD or
                abs(gyro_z) > 300) and vibration_value > 3000:
                oled.text('Crash Detected!', 0, 50)
                oled.text('CALL 100,102!', 0, 60)
                oled.show()
                trigger_event_with_retry()
        # Rest of your sensor logic...
    except Exception as e:
        print("Error in main loop:", e)