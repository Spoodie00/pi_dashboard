import random
from time import sleep
""" import board
import busio
import adafruit_sht31d
i2c = busio.I2C(board.SCL, board.SDA)
sht33 = adafruit_sht31d.SHT31D(i2c, address=0x45) """

class Sensor:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def read(self):
        max_consecutive_sensor_read_fails = 5
        output = {}
        for attempt in range(1, max_consecutive_sensor_read_fails+1):
            try:
                output = self.get_data()
            except Exception as e:
                print(f"A sensor read has failed {max_consecutive_sensor_read_fails-attempt} times due to {e}, trying again in 3 sec")
                if max_consecutive_sensor_read_fails - attempt == 0:
                    raise LookupError (f"Failed to read sensor {attempt} times due to {e}")
                sleep(3)
        return output

    def get_data(self):
        raise NotImplementedError("Custom read class not assigned to sensor")

class Read_sht3x(Sensor):
    def get_data(self):
        """ i2c = busio.I2C(board.SCL, board.SDA)
        sht33 = adafruit_sht31d.SHT31D(i2c, address)
        temp = round(sht33.temperature, 2)
        humid = round(sht33.relative_humidity, 2) """
        randnum = random.random()
        temp = randnum + random.triangular(18, 23, 20)
        humid = randnum + random.triangular(30, 60, 45)
        output = {"temp": round(temp, 5),
                "humid": round(humid, 5)}
        
        return output

class Read_ds18b20(Sensor):
    def get_data(self):
        """ path = "/sys/bus/w1/devices/"
        file_location = path + adress + "/w1_slave"
        file = open(file_location)
        data = file.read()
        file.close()
        line = data.split("\n")[1]
        temperature_data = line.split(" ")[9]
        temperature = float(temperature_data[2:])
        reading = temperature/1000 """
        randnum = random.random()
        reading = randnum + random.triangular(13, 19, 18)
        output = {"temp": round(reading, 5)}

        return output
