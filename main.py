
# ==========================================
# MAIN ENVIRONMENTAL MONITORING PROGRAM
# ==========================================

import time

from sensor import SGP41Sensor, PMS5003Sensor
from inference import calculate_index
from database import save_reading


# ==========================================
# INITIALIZE SENSORS
# ==========================================

print("Initializing environmental sensors...")

sgp41 = SGP41Sensor()
pms5003 = PMS5003Sensor()

# SGP41 runs in a background thread
# to maintain approximately 1-second sampling.
sgp41.start()

print("Sensors initialized.")
print("Press Ctrl+C to stop.\n")


# ==========================================
# MAIN MONITORING LOOP
# ==========================================

try:
    while True:

        # ==================================
        # TEMPERATURE / HUMIDITY
        # PLACEHOLDER VALUES
        # ==================================

        temperature_c = 29.0
        humidity = 35.0

        # ==================================
        # PMS5003 SENSOR
        # ==================================

        try:
            pm_data = pms5003.read()

            pm1_0 = pm_data["pm1_0"]
            pm2_5 = pm_data["pm2_5"]
            pm10 = pm_data["pm10"]

        except Exception as error:
            print("PMS5003 reading failed:", error)
            time.sleep(5)
            continue

        # ==================================
        # SGP41 SENSOR
        # ==================================

        gas_data = sgp41.read()

        if gas_data is None:
            # SGP41 may still be conditioning
            # or its sampling thread may have failed.
            if sgp41.error:
                print("SGP41 error:", sgp41.error)
            else:
                print("SGP41 warming up...")

            raw_voc = None
            raw_nox = None
            voc_index = None
            nox_index = None

        else:
            raw_voc = gas_data["raw_voc"]
            raw_nox = gas_data["raw_nox"]

            voc_index = gas_data["voc_index"]
            nox_index = gas_data["nox_index"]

        # ==================================
        # RUN INFERENCE MODEL
        # ==================================

        result = calculate_index(
            temperature_c=temperature_c,
            humidity=humidity,
            pm1_0=pm1_0,
            pm2_5=pm2_5,
            pm10=pm10,
            voc_index=voc_index,
            nox_index=nox_index
        )

        # ==================================
        # DISPLAY SENSOR VALUES
        # ==================================

        print("--------------------------------------")
        print("LOCAL ENVIRONMENTAL ASSESSMENT")
        print("--------------------------------------")

        print(f"Temperature: {temperature_c:.2f} C (test)")
        print(f"Humidity:    {humidity:.2f} % (test)")

        print(f"PM1.0:       {pm1_0:.2f} ug/m3")
        print(f"PM2.5:       {pm2_5:.2f} ug/m3")
        print(f"PM10:        {pm10:.2f} ug/m3")

        if voc_index is not None:
            print(f"VOC Index:   {voc_index:.2f}")
        else:
            print("VOC Index:   Not ready")

        if nox_index is not None:
            print(f"NOx Index:   {nox_index:.2f}")
        else:
            print("NOx Index:   Not ready")

        print()

        # ==================================
        # DISPLAY INFERENCE SCORES
        # ==================================

        print(f"Smoke score:  {result['smoke_score']}")
        print(f"Dust score:   {result['dust_score']}")
        print(f"Urban score:  {result['urban_pollution_score']}")
        print(f"Danger score: {result['general_danger_score']}")

        print(f"Danger level: {result['danger_level']}")
        print(f"Assessment:   {result['event']}")

        print()

        # ==================================
        # DISPLAY EXPLANATIONS
        # ==================================

        print("Results:")

        for item in result["results"]:
            print(f"- {item}")

        print("--------------------------------------")
        print()

        # ==================================
        # PREPARE DATABASE DATA
        # ==================================

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

        # ==================================
        # SAVE TO INFLUXDB
        # ==================================

        saved = save_reading(
            sensor_data,
            result
        )

        if saved:
            print("Database update successful")
        else:
            print("Database update failed")

        print()

        # ==================================
        # WAIT BEFORE NEXT READING
        # ==================================

        time.sleep(5)


except KeyboardInterrupt:
    print("\nMonitoring stopped by user.")


finally:
    sgp41.stop()
    print("SGP41 sampling stopped.")
