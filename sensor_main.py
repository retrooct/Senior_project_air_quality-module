
# sensor.py

import time
import threading

import board
from pms5003 import PMS5003

from adafruit_sgp41.sgp41 import SGP41
from sensirion_gas_index_algorithm.voc_algorithm import VocAlgorithm
from sensirion_gas_index_algorithm.nox_algorithm import NoxAlgorithm


# ==========================================
# SGP41 VOC / NOx SENSOR
# ==========================================

class SGP41Sensor:

    def __init__(self):
        self.i2c = board.I2C()
        self.sensor = SGP41(self.i2c)

        self.voc_algorithm = VocAlgorithm()
        self.nox_algorithm = NoxAlgorithm()

        self.latest_reading = None
        self.error = None

        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.thread = None

    def start(self):
        if self.thread and self.thread.is_alive():
            return

        self.stop_event.clear()

        self.thread = threading.Thread(
            target=self._sampling_loop,
            daemon=True
        )
        self.thread.start()

    def _sampling_loop(self):
        try:
            print("Conditioning SGP41...")

            for count in range(10):
                if self.stop_event.is_set():
                    return

                self.sensor.conditioning()
                print(f"Conditioning {count + 1}/10")

                if self.stop_event.wait(1):
                    return

            print("SGP41 conditioning complete")

            next_sample = time.monotonic()

            while not self.stop_event.is_set():

                raw_voc, raw_nox = self.sensor.measure_raw()

                voc_index = self.voc_algorithm.process(raw_voc)
                nox_index = self.nox_algorithm.process(raw_nox)

                reading = {
                    "raw_voc": float(raw_voc),
                    "raw_nox": float(raw_nox),

                    "voc_index": (
                        float(voc_index)
                        if voc_index > 0 else None
                    ),

                    "nox_index": (
                        float(nox_index)
                        if nox_index > 0 else None
                    )
                }

                with self.lock:
                    self.latest_reading = reading
                    self.error = None

                next_sample += 1.0

                # Avoid repeated immediate samples if delayed
                now = time.monotonic()
                if next_sample < now:
                    next_sample = now + 1.0

                if self.stop_event.wait(
                    max(0, next_sample - now)
                ):
                    break

        except Exception as error:
            with self.lock:
                self.error = str(error)
                self.latest_reading = None

            print("SGP41 error:", error)

    def read(self):
        with self.lock:
            if self.latest_reading is None:
                return None

            return self.latest_reading.copy()

    def stop(self):
        self.stop_event.set()

        if self.thread:
            self.thread.join(timeout=2)


# ==========================================
# PMS5003 PARTICULATE SENSOR
# ==========================================

class PMS5003Sensor:

    def __init__(self):
        self.sensor = PMS5003(
            device="/dev/serial0",
            baudrate=9600
        )

    def read(self):
        data = self.sensor.read()

        return {
            "pm1_0": float(data.pm_ug_per_m3(1.0)),
            "pm2_5": float(data.pm_ug_per_m3(2.5)),
            "pm10": float(data.pm_ug_per_m3(10))
        }

        
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


