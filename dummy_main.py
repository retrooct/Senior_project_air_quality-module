
# dummy_main.py
# Test environmental inference using simulated sensor values

from inference import calculate_index
from database import save_reading


def get_number(name, default):
    """Ask for a sensor value, using a default if left blank."""
    while True:
        value = input(f"{name} [{default}]: ").strip()

        if not value:
            return float(default)

        try:
            return float(value)
        except ValueError:
            print("Please enter a valid number.")


def main():

    print("======================================")
    print("AIR QUALITY SIMULATION")
    print("======================================")
    print("Enter simulated sensor measurements.")
    print("Press Enter to accept a default value.\n")

    while True:

        # ----------------------------------
        # Simulated sensor measurements
        # ----------------------------------

        temperature_c = get_number("Temperature (C)", 25)
        humidity = get_number("Humidity (%)", 40)

        pm1_0 = get_number("PM1.0 (ug/m3)", 5)
        pm2_5 = get_number("PM2.5 (ug/m3)", 12)
        pm10 = get_number("PM10 (ug/m3)", 20)

        voc_index = get_number("VOC Index", 100)
        nox_index = get_number("NOx Index", 1)

        # ----------------------------------
        # Run the inference model
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
        # Display results
        # ----------------------------------

        print("\n======================================")
        print("SIMULATED ENVIRONMENTAL ASSESSMENT")
        print("======================================")

        print(f"PM1.0:          {pm1_0:.2f} ug/m3")
        print(f"PM2.5:          {pm2_5:.2f} ug/m3")
        print(f"PM10:           {pm10:.2f} ug/m3")

        print(f"VOC Index:      {voc_index:.2f}")
        print(f"NOx Index:      {nox_index:.2f}")

        print()
        print("PM2.5 AQI-like:", result["pm25_aqi"])
        print("AQI Category:  ", result["pm25_aqi_category"])

        print()
        print("VOC State:     ", result["voc_state"])
        print("NOx State:     ", result["nox_state"])

        print()
        print("Smoke Score:   ", result["smoke_score"])
        print("Dust Score:    ", result["dust_score"])
        print("Urban Score:   ", result["urban_pollution_score"])
        print("Danger Score:  ", result["general_danger_score"])
        print("Danger Level:  ", result["danger_level"])
        print("Event:         ", result["event"])

        print("\nExplanations:")

        for item in result["results"]:
            print("-", item)

        # ----------------------------------
        # Optional InfluxDB write
        # ----------------------------------

        choice = input(
            "\nSave simulated values to InfluxDB? (y/n): "
        ).strip().lower()

        if choice == "y":

            sensor_data = {
                "temperature_c": temperature_c,
                "humidity": humidity,
                "pm1_0": pm1_0,
                "pm2_5": pm2_5,
                "pm10": pm10,
                "voc_index": voc_index,
                "nox_index": nox_index
            }

            success = save_reading(sensor_data, result)

            if success:
                print("Simulated data saved to InfluxDB.")
            else:
                print("InfluxDB write failed.")

        # ----------------------------------
        # Repeat or exit
        # ----------------------------------

        again = input(
            "\nTest another scenario? (y/n): "
        ).strip().lower()

        if again != "y":
            print("Simulation finished.")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSimulation stopped.")
