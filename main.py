# main.py

import time
from inference import calculate_index


while True:
    # ==========================================
    # SENSOR VALUES
    # For now these are placeholder test values.
    # Later, replace these with real sensor readings.
    # ==========================================

    temperature_c = 25.4
    humidity = 48.0

    pm1_0 = 12.0
    pm2_5 = 42.5
    pm10 = 60.0

    voc_index = 165.0
    nox_index = 80.0

    # ==========================================
    # RUN INFERENCE MODEL
    # ==========================================

    result = calculate_index(
        temperature_c=temperature_c,
        humidity=humidity,
        pm1_0=pm1_0,
        pm2_5=pm2_5,
        pm10=pm10,
        voc_index=voc_index,
        nox_index=nox_index
    )

    # ==========================================
    # DISPLAY SENSOR VALUES
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

    # ==========================================
    # DISPLAY INFERENCE SCORES
    # ==========================================

    print(f"Smoke score:       {result['smoke_score']}")
    print(f"Dust score:        {result['dust_score']}")
    print(f"Urban score:       {result['urban_pollution_score']}")
    print(f"Danger score:      {result['general_danger_score']}")
    print(f"Danger level:      {result['danger_level']}")
    print(f"Assessment:        {result['event']}")
    print()

    # ==========================================
    # DISPLAY REASONING RESULTS
    # ==========================================

    print("Results:")

    if result["results"]:
        for item in result["results"]:
            print(f"- {item}")
    else:
        print("- No major warning signs detected")

    print("--------------------------------------")
    print()

    time.sleep(5)
