import glob
import time

# Find the DS18B20
devices = glob.glob('/sys/bus/w1/devices/28-*')

if not devices:
    print("No DS18B20 found.")
    exit()

device_file = devices[0] + '/w1_slave'

while True:
    with open(device_file, 'r') as f:
        lines = f.readlines()

    # Check that the reading is valid
    if lines[0].strip().endswith('YES'):
        # Find the temperature value
        temp_pos = lines[1].find('t=')

        if temp_pos != -1:
            temp_c = float(lines[1][temp_pos + 2:]) / 1000.0
            temp_f = temp_c * 9 / 5 + 32

            print(f"Temperature: {temp_c:.2f} °C ({temp_f:.2f} °F)")

    time.sleep(2)
