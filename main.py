# main.py

import time
from inference import calculate_indices


while True:
    # ==========================================
    # SENSOR VALUES
    # Later these should come from your sensor files.
    # ==========================================

    temperature_c = 25.4
    humidity = 48.0

    pm1_0 = 12.0
    pm2_5 = 42.5
    pm10 = 60.0

    voc_index = 165.0
    nox_index = 80.0

    co_ppm = 0.0          # Use 0.0 if you do not have a CO sensor yet
    wind_speed = 0.0      # Use 0.0 if you do not have wind sensor yet

    # ==========================================
    # RUN INFERENCE MODEL
    # ==========================================

    result = calculate_indices(
        temperature_c=temperature_c,
        humidity=humidity,
        pm1_0=pm1_0,
        pm2_5=pm2_5,
        pm10=pm10,
        voc_index=voc_index,
        nox_index=nox_index,
        co_ppm=co_ppm,
        wind_speed=wind_speed
    )

    # ==========================================
    # DISPLAY RESULTS
    # ==========================================

    print("--------------------------------------")
    print("LOCAL ENVIRONMENTAL ASSESSMENT")
    print("--------------------------------------")
    print(f"Temperature: {temperature_c:.2f} C")
    print(f"Humidity:    {humidity:.2f} %")
    print(f"PM1.0:       {pm1_0:.2f} ug/m3")
    print(f"PM2.5:       {pm2_5:.2f} ug/m3")
    print(f"PM10:        {pm10:.2f} ug/m3")
    print(f"VOC Index:   {voc_index:.2f}")
    print(f"NOx Index:   {nox_index:.2f}")
    print()
    print(f"Smoke score:       {result['smoke_score']}")
    print(f"Dust score:        {result['dust_score']}")
    print(f"Urban score:       {result['urban_pollution_score']}")
    print(f"Danger score:      {result['general_danger_score']}")
    print(f"Danger level:      {result['danger_level']}")
    print(f"Assessment:        {result['event']}")
    print()
    print("Evidence:")

    for item in result["evidence"]:
        print(f"- {item}")

    print("--------------------------------------")
    print()

    time.sleep(5)
