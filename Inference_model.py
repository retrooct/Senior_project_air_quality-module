import temp_sense.py 
import

float temperature_c
float humidity
float pm1_0
pm2_5
pm10
voc_index
nox_index
co_ppm

while True:

    temperature_c = read_temperature()
    humidity = read_humidity()
    pm1_0, pm2_5, pm10 = read_particles()
    voc_index, nox_index = read_gases()

    result = infer_event(
        temperature_c,
        humidity,
        pm2_5,
        pm10,
        voc_index,
        nox_index
    )

    print(result)

    time.sleep(10)


if pm25_is_high and co_is_high:
    possible_smoke = True

if pm10_is_high and wind_is_high and pm25_is_low:
    possible_dust = True

if pm25_is_high and no2_is_high and co_is_high:
    possible_urban_combustion = True

if smoke_score >= 3:
    event = "possible smoke event"

elif dust_score >= 3:
    event = "possible dust event"

elif urban_pollution_score >= 3:
    event = "possible combustion/urban pollution"

else:
    event = "no significant event detected"
