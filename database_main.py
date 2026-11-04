
import os
import influxdb_client

from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS


# ==========================================
# INFLUXDB CONFIGURATION
# ==========================================

org = "Senior_project"
url = "http://localhost:8086"
bucket = "weather_data"


# ==========================================
# SAVE SENSOR AND INFERENCE DATA
# ==========================================

def save_reading(sensor_data, result):

    token = os.environ.get("INFLUXDB_TOKEN")

    if not token:
        print("Error: INFLUXDB_TOKEN is not set")
        return False

    # Create measurement
    point = (
        Point("air_quality")
        .tag("device", "raspberry_pi")
    )

    # --------------------------------------
    # SENSOR READINGS
    # --------------------------------------

    sensor_fields = [
        "temperature_c",
        "humidity",
        "pm1_0",
        "pm2_5",
        "pm10",
        "raw_voc",
        "raw_nox",
        "voc_index",
        "nox_index"
    ]

    for name in sensor_fields:
        value = sensor_data.get(name)

        if value is not None:
            point = point.field(
                name,
                float(value)
            )

    # --------------------------------------
    # INFERENCE SCORES
    # --------------------------------------

    inference_fields = [
        "smoke_score",
        "dust_score",
        "urban_pollution_score",
        "general_danger_score",
        "particle_pollution_score",
        "coarse_particle_score",
        "voc_event_score",
        "nox_event_score"
    ]

    for name in inference_fields:
        value = result.get(name)

        if value is not None:
            point = point.field(
                name,
                int(value)
            )

    # --------------------------------------
    # PM10 / PM2.5 RATIO
    # --------------------------------------

    ratio = result.get("pm10_pm25_ratio")

    if ratio is not None:
        point = point.field(
            "pm10_pm25_ratio",
            float(ratio)
        )

    # --------------------------------------
    # EVENT CLASSIFICATION
    # --------------------------------------

    event = result.get("event")

    if event is not None:
        point = point.field(
            "event",
            str(event)
        )

    # --------------------------------------
    # DANGER LEVEL
    # --------------------------------------

    danger_level = result.get("danger_level")

    if danger_level is not None:
        point = point.field(
            "danger_level",
            str(danger_level)
        )

    # --------------------------------------
    # INFERENCE EXPLANATIONS
    # --------------------------------------

    explanations = result.get("results")

    if explanations:
        point = point.field(
            "results",
            "\n".join(map(str, explanations))
        )

    # --------------------------------------
    # WRITE TO INFLUXDB
    # --------------------------------------

    try:
        with influxdb_client.InfluxDBClient(
            url=url,
            token=token,
            org=org,
            timeout=10000
        ) as client:

            with client.write_api(
                write_options=SYNCHRONOUS
            ) as write_api:

                write_api.write(
                    bucket=bucket,
                    org=org,
                    record=point
                )

        print(
            "InfluxDB: Sensor and inference data saved"
        )

        return True

    except Exception as error:

        print(
            "InfluxDB write failed:",
            error
        )

        return False
