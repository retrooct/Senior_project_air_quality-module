import glob
import time

devices = glob.glob('/sys/bus/w1/devices/28-*')

if not devices:
    print("No DS18B20 detected.")
    exit()

device_folder = devices[0]
device_file = device_folder + '/w1_slave'

print("Sensor found:", device_folder)
