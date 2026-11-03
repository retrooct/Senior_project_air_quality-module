"""Read SGP41 VOC/NOx data and send it to InfluxDB."""

import time
from getpass import getpass

import board
from adafruit_sgp41.sgp41 import SGP41
from sensirion_gas_index_algorithm.voc_algorithm import VocAlgorithm
from sensirion_gas_index_algorithm.nox_algorithm import NoxAlgorithm

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


print("InfluxDB Connection Setup")
print()

computer_ip = input("Enter your computer IPv4 address: ").strip()
organization = input(
    "Enter your InfluxDB organization [weather-project]: "
).strip() or "weather-project"
bucket = input(
    "Enter your InfluxDB bucket [weather-data]: "
).strip() or "weather-data"
token = getpass("Paste your NEW write-only API token: ").strip()

influx_url = f"http://{computer_ip}:8086"

influx_client = InfluxDBClient(
    url=influx_url,
    token=token,
    org=organization
)

write_api = influx_client.write_api(write_options=SYNCHRONOUS)

print()
print(f"Connecting to {influx_url}...")

try:
    if not influx_client.ping():
        raise ConnectionError("InfluxDB did not respond.")

    print("InfluxDB connection is working.")

except Exception as error:
    influx_client.close()
    raise SystemExit(f"InfluxDB connection failed: {error}")


voc_algorithm = VocAlgorithm()
nox_algorithm = NoxAlgorithm()

i2c = board.I2C()
sensor = SGP41(i2c)

print()
print("Conditioning the SGP41 sensor...")

for count in range(10):
    sensor.conditioning()
    print(f"Conditioning: {count + 1}/10")
    time.sleep(1)

print()
print("Sensor is ready.")
print("Press Ctrl+C to stop the program.")
print()


try:
    while True:
        raw_voc = sensor.raw_voc
        raw_nox = sensor.raw_nox

        voc_index = voc_algorithm.process(raw_voc)
        nox_index = nox_algorithm.process(raw_nox)

        if voc_index == 0:
            voc_state = "Warming Up"
        elif voc_index <= 100:
            voc_state = "Stable"
        elif voc_index <= 250:
            voc_state = "Slight Deterioration"
        elif voc_index <= 400:
            voc_state = "Distinct Deterioration"
        else:
            voc_state = "Intense Deterioration"

        if nox_index == 0:
            nox_state = "Warming Up"
        elif nox_index == 1:
            nox_state = "No NOx Gases Present"
        elif nox_index <= 20:
            nox_state = "Minimal NOx Gases Present"
        elif nox_index <= 150:
            nox_state = "Slight NOx Presence"
        elif nox_index <= 300:
            nox_state = "Distinct NOx Presence"
        else:
            nox_state = "Intense NOx Presence"

        point = (
            Point("air_quality")
            .tag("device", "voc_pi")
            .field("raw_voc", float(raw_voc))
            .field("voc_index", float(voc_index))
            .field("voc_state", voc_state)
            .field("raw_nox", float(raw_nox))
            .field("nox_index", float(nox_index))
            .field("nox_state", nox_state)
        )

        try:
            write_api.write(
                bucket=bucket,
                org=organization,
                record=point
            )

            print("----------------------------------------")
            print(f"Raw VOC:   {raw_voc}")
            print(f"VOC Index: {voc_index} | {voc_state}")
            print(f"Raw NOx:   {raw_nox}")
            print(f"NOx Index: {nox_index} | {nox_state}")
            print("Status: Reading sent to InfluxDB")

        except Exception as error:
            print("----------------------------------------")
            print(f"Status: Could not send reading: {error}")

        time.sleep(1)


except KeyboardInterrupt:
    print()
    print("Program stopped.")


finally:
    write_api.close()
    influx_client.close()
    print("InfluxDB connection closed.")
