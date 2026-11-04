
# main.py

import time

from sensor import SGP41Sensor, PMS5003Sensor
from inference import calculate_index
from database import save_reading


# ==========================================
# SENSOR INITIALIZATION
# ==========================================

print("Initializing sensors...")

sgp41 = SGP41Sensor()
pms5003 = PMS5003Sensor()

sgp41.start()

print("Sensors initialized")
print("Press Ctrl+C to stop\n")


# ==========================================
# FORMATTING HELPER
# ==========================================

def format_value(value, decimals=2):
    if value is None:
        return "Not available"

    return f"{value:.{decimals}f}"


# ==========================================
# MAIN MONITORING LOOP
# ==========================================

try:

    while True:

        # ----------------------------------
        # Temperature and humidity
        # ----------------------------------

        # Replace these when a real sensor
        # is connected.
        temperature_c = None
        humidity = None

        # ----------------------------------
        # PMS5003 measurements
        # ----------------------------------

        try:
            pm_data = pms5003.read()

            pm1_0 = pm_data["pm1_0"]
            pm2_5 = pm_data["pm2_5"]
            pm10 = pm_data["pm10"]

        except Exception as error:
            print("PMS5003 reading failed:", error)
            time.sleep(5)
            continue

        # ----------------------------------
        # SGP41 measurements
        # ----------------------------------

        gas_data = sgp41.read()

        if gas_data is None:

            raw_voc = None
            raw_nox = None
            voc_index = None
            nox_index = None

            if sgp41.error:
                print("SGP41 error:", sgp41.error)
            else:
                print("SGP41 conditioning...")

        else:

            raw_voc = gas_data["raw_voc"]
            raw_nox = gas_data["raw_nox"]

            voc_index = gas_data["voc_index"]
            nox_index = gas_data["nox_index"]

        # ----------------------------------
        # Run inference model
        # ----------------------------------

        result = calculate_index(
            temperature_c=temperature_c,
            humidity=humidity,
            pm1_0=pm1_0,
            pm2_5=pm2_5,
            pm10=pm10,
            voc_index=voc_index,
            nox_index=nox_index
        )

        # ----------------------------------
        # Display measurements
        # ----------------------------------

        print("======================================")
        print("LOCAL ENVIRONMENTAL ASSESSMENT")
        print("======================================")

        print(
            "Temperature:",
            format_value(temperature_c),
            "C"
        )

        print(
            "Humidity:",
            format_value(humidity),
            "%"
        )

        print(f"PM1.0:  {pm1_0:.2f} ug/m3")
        print(f"PM2.5:  {pm2_5:.2f} ug/m3")
        print(f"PM10:   {pm10:.2f} ug/m3")

        print()

        # ----------------------------------
        # AQI-like assessment
        # ----------------------------------

        print("PM2.5 AQI-LIKE ASSESSMENT")

        print(
            "AQI-like value:",
            result["pm25_aqi"]
        )

        print(
            "AQI category:",
            result["pm25_aqi_category"]
        )

        print()

        # ----------------------------------
        # VOC / NOx assessment
        # ----------------------------------

        print("GAS SENSOR ASSESSMENT")

        print(
            "Raw VOC:",
            format_value(raw_voc, 0)
        )

        print(
            "VOC Index:",
            format_value(voc_index, 0)
        )

        print(
            "VOC State:",
            result["voc_state"]
        )

        print()

        print(
            "Raw NOx:",
            format_value(raw_nox, 0)
        )

        print(
            "NOx Index:",
            format_value(nox_index, 0)
        )

        print(
            "NOx State:",
            result["nox_state"]
        )

        print()

        # ----------------------------------
        # Inference assessment
        # ----------------------------------

        print("ENVIRONMENTAL INFERENCE")

        print(
            "Smoke score:",
            result["smoke_score"]
        )

        print(
            "Dust score:",
            result["dust_score"]
        )

        print(
            "Urban score:",
            result["urban_pollution_score"]
        )

        print(
            "General danger score:",
            result["general_danger_score"]
        )

        print(
            "Danger level:",
            result["danger_level"]
        )

        print(
            "Event:",
            result["event"]
        )

        print()

        # ----------------------------------
        # Explanation messages
        # ----------------------------------

        print("REASONING RESULTS")

        for explanation in result["results"]:
            print("-", explanation)

        print("======================================")
        print()

        # ----------------------------------
        # Prepare sensor data
        # ----------------------------------

        sensor_data = {
            "temperature_c": temperature_c,
            "humidity": humidity,

            "pm1_0": pm1_0,
            "pm2_5": pm2_5,
            "pm10": pm10,

            "raw_voc": raw_voc,
            "raw_nox": raw_nox,

            "voc_index": voc_index,
            "nox_index": nox_index
        }

        # ----------------------------------
        # Save to InfluxDB
        # ----------------------------------

        saved = save_reading(
            sensor_data,
            result
        )

        if saved:
            print("Database update successful")
        else:
            print("Database update failed")

        print()

        # ----------------------------------
        # Wait five seconds
        # ----------------------------------

        time.sleep(5)


except KeyboardInterrupt:

    print("\nMonitoring stopped by user")


finally:

    sgp41.stop()
    print("SGP41 sampling stopped")
