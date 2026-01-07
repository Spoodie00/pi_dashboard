import random
from time import sleep
import board
import busio
import adafruit_sht31d
i2c = busio.I2C(board.SCL, board.SDA)

class Sensor:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def read(self, address):
        max_consecutive_sensor_read_fails = 5
        output = {}
        for attempt in range(1, max_consecutive_sensor_read_fails+1):
            try:
                output = self.get_data(address)
                return output
            except Exception as e:
                print(f"A sensor with adress {address} read has failed {attempt} times due to {e}, trying again in 3 sec")
                if max_consecutive_sensor_read_fails - attempt == 0:
                    raise LookupError (f"Failed to read sensor {attempt} times due to {e}")
                sleep(3)

    def get_data(self):
        raise NotImplementedError("Custom read class not assigned to sensor")

class Read_sht3x(Sensor):
    def __init__(self, **params):
        super().__init__(**params)
        # 1. SETUP HAPPENS ONCE HERE
        # We use a global i2c object so we don't restart the bus
        self.device = adafruit_sht31d.SHT31D(i2c, self.address)

    def get_data(self, address):
        output = {"temperature": round(self.device.temperature, 4),
                "humidity": round(self.device.relative_humidity, 4)}
        return output

class Read_ds18b20(Sensor):
    def __init__(self, **params):
        super().__init__(**params)
        # Pre-calculate path so we don't do string math every loop
        self.path = f"/sys/bus/w1/devices/{self.address}/w1_slave"

    def get_data(self, address):
        with open(self.path, "r") as f:
            data = f.read()
        temp_string = data.split("t=")[1]
        return {"temperature": round(float(temp_string) / 1000, 4)}
