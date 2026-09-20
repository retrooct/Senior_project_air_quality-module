import glob


def read_temperature_c() -> float | None:
    """
    Reads the DS18B20 temperature sensor once.

    Returns:
        temperature in Celsius as a float,
        or None if the sensor is not found or the reading is invalid.
    """

    # Find the DS18B20 device folder
    devices = glob.glob("/sys/bus/w1/devices/28-*")

    if not devices:
        return None

    device_file = devices[0] + "/w1_slave"

    with open(device_file, "r") as f:
        lines = f.readlines()

    # Check that the reading is valid
    if not lines[0].strip().endswith("YES"):
        return None

    # Find the temperature value
    temp_pos = lines[1].find("t=")

    if temp_pos == -1:
        return None

    raw_temp = lines[1][temp_pos + 2:].strip()
    temp_c = float(raw_temp) / 1000.0

    return temp_c


def read_temperature_f() -> float | None:
    """
    Reads the DS18B20 temperature sensor once
    and returns Fahrenheit.
    """

    temp_c = read_temperature_c()

    if temp_c is None:
        return None

    temp_f = temp_c * 9 / 5 + 32
    return temp_f
