import os
import time
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# InfluxDB connection settings
url = "http://172.20.10.4:8086"
org = "Senior_project"
bucket = "weather_data"

token = os.environ.get("INFLUXDB_TOKEN")

if not token:
    raise RuntimeError("INFLUXDB_TOKEN is not set")

# Create the InfluxDB connection
client = InfluxDBClient(
    url=url,
    token=token,
    org=org
)

# Create the write API
write_api = client.write_api(write_options=SYNCHRONOUS)

# Send test sensor data
point = (
    Point("air_quality")
    .tag("device", "raspberry_pi")
    .field("temperature_c", 25.4)
    .field("humidity", 48.0)
    .field("pm1_0", 12.0)
    .field("pm2_5", 42.5)
    .field("pm10", 60.0)
    .field("voc_index", 165.0)
    .field("nox_index", 80.0)
)

write_api.write(
    bucket=bucket,
    org=org,
    record=point
)

print("Sensor data successfully sent to InfluxDB!")

client.close()
