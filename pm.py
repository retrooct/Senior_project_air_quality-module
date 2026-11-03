#!/usr/bin/env python3

from pms5003 import PMS5003
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import time

# ==================================================
# InfluxDB configuration
# ==================================================

#INFLUX_URL = "http://10.101.159.146:8086"
INFLUX_ORG = "weather-project"
INFLUX_BUCKET = "weather-data"
#INFLUX_TOKEN = "H7X9-gZBXHQGoW3JMkNAEI6vcIQ1KW38qlX_rEam1ZBRhv0nDufntJGwibQnnNjYWJUuUl8EnPBINFwWHm-Bog=="
INFLUX_URL = "http://10.100.148.111:8086"
INFLUX_TOKEN = "cpBE8tlklY_b1UymBIVsV6xwY-W2oLyiD7rRL9w3hG2_vQ0_s1t5RuRkxO19k_gOvakyDYaYD0PnuSelj84TnA=="
# ==================================================
# PM2.5 AQI calculation
# ==================================================

def calculate_pm25_aqi(concentration):
    breakpoints = [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 350.4, 301, 400),
        (350.5, 500.4, 401, 500)
    ]

    concentration = round(concentration, 1)

    for c_low, c_high, i_low, i_high in breakpoints:
        if c_low <= concentration <= c_high:
            aqi = (
                ((i_high - i_low) / (c_high - c_low))
                * (concentration - c_low)
	    + i_low
            )

            return int(round(aqi))

    return 500


def get_aqi_category(aqi):
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Moderate"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    elif aqi <= 200:
        return "Unhealthy"
    elif aqi <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"


# ==================================================
# PMS5003 sensor setup
# ==================================================

pms5003 = PMS5003(
    device="/dev/serial0",
    baudrate=9600
)

# ==================================================
# InfluxDB connection
# ==================================================

client = InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG,
    timeout=10000
)

write_api = client.write_api(write_options=SYNCHRONOUS)
# ==================================================
# Read and send sensor data
# ==================================================

try:
    print("Starting PMS5003 Air Quality Monitor")
    print(f"Sending data to: {INFLUX_URL}")
    print("Press Ctrl+C to stop.\n")

    while True:
        try:
            # Read the PMS5003 sensor
            data = pms5003.read()

            pm1 = float(data.pm_ug_per_m3(1.0))
            pm25 = float(data.pm_ug_per_m3(2.5))
            pm10 = float(data.pm_ug_per_m3(10))

            aqi = calculate_pm25_aqi(pm25)
            category = get_aqi_category(aqi)

            print(	
    f"PM1.0: {pm1} ug/m3 | "
                f"PM2.5: {pm25} ug/m3 | "
                f"PM10: {pm10} ug/m3 | "
                f"AQI: {aqi} | "
                f"Category: {category}"
            )

            # Create the InfluxDB data point
            point = (
                Point("air_quality")
                .tag("sensor", "PMS5003")
                .tag("device", "raspberry-pi")
                .field("pm1", pm1)
                .field("pm25", pm25)
                .field("pm10", pm10)
                .field("aqi", aqi)
                .field("category", category)
            )

            # Send the point to InfluxDB
            write_api.write(
                bucket=INFLUX_BUCKET,
                org=INFLUX_ORG,
                record=point
            )

            print("Successfully saved to InfluxDB.\n")

        except Exception as error:
            print(f"Error reading or sending data: {error}\n")

        time.sleep(5)

except KeyboardInterrupt:
    print("\nMonitoring stopped by user.")

finally:
    client.close()
    print("InfluxDB connection closed.")


