import storage_functions
import sensors
import datetime
import time

print("Running Logging.py")
ds18b20_readings = []
sht33_temp_readings = []
sht33_humid_readings = []


def avg_data(list):  
  num = sum(list)/len(list)
  rounded_num = round(num, 2)
  storage_ready_num = f"{rounded_num:.2f}"
  return storage_ready_num

if __name__ == "__main__":
  while True:
    sht33 = sensors.sht33_reading
    for attempt in range(3):
      try:
            #storing data in lists for processing
            ds18b20_readings.append(sensors.get_ds18b20_temp("28-3cb7e3819e17"))
            sht33_temp_readings.append(sensors.sht33_reading()[0])
            sht33_humid_readings.append(sensors.sht33_reading()[1])
            break
      except Exception as e:
        print(f"A sensor read failed due to {e} trying again in 3 sec")
        time.sleep(3)

    #long term storage
    #unixtime in UTC
    presentDate = datetime.datetime.now()
    timestamp = int(datetime.datetime.timestamp(presentDate))

    #store data in sqlite and restart count
    if len(ds18b20_readings) > 14:
      #sqlite command
      table = "long_term_data(date_time, ds18b20_floor, sht33_wall_temp, sht33_wall_humid)"
      len_of_table = "(?, ?, ?, ?)"
      data = (timestamp, avg_data(ds18b20_readings), avg_data(sht33_temp_readings), avg_data(sht33_humid_readings))  

      storage_functions.insert_into_table(table, len_of_table, data)
      ds18b20_readings = []
      sht33_temp_readings = []
      sht33_humid_readings = []
      print("logged some readings")
    

    #keep logging
    print("checked temp and now sleeping for 60 sec")
    time.sleep(60)
