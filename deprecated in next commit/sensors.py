import os
import board
import busio
import adafruit_sht31d
i2c = busio.I2C(board.SCL, board.SDA)
#finner sensorene i systemet og returnerer navnet
#It this used for anything at all?
def sensor(directory):
  output = []
  for device in os.listdir(directory):
    if "w1_bus_master" not in device:
      output.append(device)
  return output

#Refactor this at some point please
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
  data = read_ds18b20(path, probeid)
  return round(data, 4)

#soon to be deprecated
def sht33_temp(address):
  sht33 = adafruit_sht31d.SHT31D(i2c, address)
  temp = round(sht33.temperature, 4)
  return temp

#soon to be deprecated
def sht33_humid(address):
  sht33 = adafruit_sht31d.SHT31D(i2c, address)
  humid = round(sht33.relative_humidity, 2)
  return round(humid, 2)

def read_sht3x(address):
  i2c = busio.I2C(board.SCL, board.SDA)
  sht33 = adafruit_sht31d.SHT31D(i2c, address)
  temp = round(sht33.temperature, 2)
  humid = round(sht33.relative_humidity, 2)
  output = {"temp": temp,
            "humid": humid}
  return output

if __name__ == "__main__":
    pass
