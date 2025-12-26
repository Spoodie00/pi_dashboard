import os
import random
""" import board
import busio
import adafruit_sht31d
i2c = busio.I2C(board.SCL, board.SDA)
sht33 = adafruit_sht31d.SHT31D(i2c, address=0x45) """
tss = 1
#finner sensorene i systemet og returnerer navnet
def sensor(directory):
	for device in os.listdir(directory):
		output = []
		if "w1_bus_master" not in device:
			output.append(device)
	return output

def read_ds18b20(path, probe):
  #finner pathen til temperaturfila
  file_location = path + probe + "/w1_slave"

  #åpner, leser og lukker file
  produced_file = open(file_location)

  reading = produced_file.read()
  produced_file.close()
  #litt triksing med lest tekst for å isolere kun temperaturen, og returnerer i celsius
  second_line = reading.split("\n")[1]
  temperature_data = second_line.split(" ")[9]
  temperature = float(temperature_data[2:])
  value = temperature/1000
  return value

def get_ds18b20_temp(probeid):
  path = "/sys/bus/w1/devices/"
  #data = read_ds18b20(path, probeid)
  #temp = round(data, 2)
  randnum = random.random()
  temp = randnum + random.triangular(13, 19, 18)
  return round(temp, 2)

def sht33_temp():
  #temp = round(sht33.temperature, 2)
  randnum = random.random()
  temp = randnum + random.triangular(18, 23, 20)
  return round(temp, 2)

def sht33_humid():
  #humid = round(sht33.relative_humidity, 2)
  randnum = random.random()
  humid = randnum + random.triangular(30, 60, 45)
  return round(humid, 2)

if __name__ == "__main__":
   import statistics
   import math
   print(statistics.stdev([17.224, 17.112666666666666, 16.839333333333332, 16.306666666666665, 17.274, 17.074, 16.930666666666667]))
   val = 0.6466163809523864/6
   print(math.sqrt(val))
