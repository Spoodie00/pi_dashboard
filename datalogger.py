import storage_functions
import sensors
from datetime import datetime, timedelta
import time
import sqlite3
import statistics

def get_average(list):  
  num = sum(list)/len(list)
  return prettify_value(num)

def prettify_value(number):
  rounded_num = round(number, 2)
  ready_num = f"{rounded_num:.2f}"
  return ready_num

max_delta_floor_wall = 0
min_delta_floor_wall = 0
num_readings = 0
floor_temps = []
wall_temps = []
wall_humidities = []
live_data = []
sleep_time = 2
start_time = time.time()

while True:
  minimum_number_of_readings = 15

  current_day = datetime.now()

  date_today_iso = current_day.date().isoformat()

  now = int(current_day.timestamp())

  day_ago = current_day - timedelta(days=1)
  day_ago_iso = day_ago.date().isoformat()

  week_ago = current_day - timedelta(days=7)
  week_ago_iso = week_ago.date().isoformat()

  num_consecutive_fails = 0

  for attempt in range(5):
    try:
          ds18b20_floor_temp = sensors.get_ds18b20_temp("28-3cb7e3819e17")
          sht33_wall_temp = sensors.sht33_temp()
          sht33_wall_humid = sensors.sht33_humid()

          floor_temps.append(ds18b20_floor_temp)
          wall_temps.append(sht33_wall_temp)
          wall_humidities.append(sht33_wall_humid)

          delta_floor_wall = abs(ds18b20_floor_temp - sht33_wall_temp)
          if max_delta_floor_wall < delta_floor_wall:
             max_delta_floor_wall = delta_floor_wall

          if min_delta_floor_wall > delta_floor_wall:
             min_delta_floor_wall = delta_floor_wall

          live_data_values = (("ds18b20_floor_temp", prettify_value(ds18b20_floor_temp)), ("sht33_wall_temp", prettify_value(sht33_wall_temp)), ("sht33_wall_humid", prettify_value(sht33_wall_humid)))

          for sensor, value in live_data_values:
             live_data.append((now, sensor, value))

          num_readings += 1
          print(f"Number of lines logged: {num_readings} out of {minimum_number_of_readings}")
          break
    
    except Exception as e:
      num_consecutive_fails += 1
      print(f"A sensor read has failed {num_consecutive_fails} times due to {e}, trying again in 3 sec")
      time.sleep(3)

  if num_readings >= minimum_number_of_readings:
      connection = sqlite3.connect('/home/mads/Documents/Temp_logging_project/logging_data_copy.db')
      cursor = connection.cursor()

      cursor.execute("BEGIN;")

      cursor.executemany(f"""
                INSERT INTO liveData (id, ts, reading) 
                VALUES (?, ?, ?)
                """, live_data)
      
      sensor_values = [
        ("ds18b20_floor", floor_temps),
        ("sht33_temp_wall", wall_temps),
        ("sht33_humid_wall", wall_humidities),
        ]   
      
      for sensor, values in sensor_values:

        db_id = sensor
        db_date = date_today_iso
        db_numReadings = 1
        db_aggregate = prettify_value(sum(values))
        db_variance = prettify_value(statistics.variance(values))
        db_maxDelta = prettify_value(max_delta_floor_wall)
        db_minDelta = prettify_value(min_delta_floor_wall)
        db_average = get_average(values)
        db_unix = now

        daily_aggregate = (db_id, db_date, db_numReadings, db_aggregate, db_variance, db_maxDelta, db_minDelta)
        quarter_hour_average = (db_id, db_unix, db_average)

        cursor.execute(f"""
                      INSERT INTO dailyAggregate (id, date, numReadings, aggregate, variance, maxDelta, minDelta) 
                      VALUES (?, ?, ?, ?, ?, ?, ?)
                      ON CONFLICT(id, date) DO UPDATE SET
                      numReadings = numReadings + excluded.numReadings,
                      aggregate = aggregate + excluded.aggregate,
                      variance = variance + excluded.variance,
                      maxDelta = MAX(maxDelta, excluded.maxDelta),
                      minDelta = MAX(minDelta, excluded.minDelta); 
                      """, daily_aggregate)

        cursor.execute(f"""
                      INSERT INTO weekBuffer (id, ts, reading)
                      VALUES (?, ?, ?)
                      """, quarter_hour_average)
      
      cursor.execute(f"""
                    DELETE FROM liveData 
                    WHERE ts < {day_ago_iso}
                    """)       
      
      cursor.execute(f"""
                    DELETE FROM weekBuffer 
                    WHERE ts < {week_ago_iso}
                    """) 

      #cursor.execute(f"""
      #              INSERT INTO long_term_data (date_time, ds18b20_floor, sht33_wall_temp, sht33_wall_humid)
      #              VALUES (?, ?, ?, ?)
      #              """, quarter_hour_average)

      connection.commit()
      connection.close()
      print(f"Pushed to database, total time since last push: desired = {14*sleep_time}, actual = {time.time() - start_time}")

      num_readings = 0
      floor_temps = []
      wall_temps = []
      wall_humidities = []
      live_data = []
      start_time = time.time()

  time.sleep(sleep_time)

while False:
  floor_temp_list = []
  wall_temp_list = []
  wall_humidity_list = []
  presentDate = datetime.now()
  unix_timestamp = int(datetime.timestamp(presentDate))
  num_consecutive_fails = 0

  for attempt in range(5):
    try:
          floor_temp_list.append(sensors.get_ds18b20_temp("28-3cb7e3819e17"))
          wall_temp_list.append(sensors.sht33_temp)
          wall_humidity_list.append(sensors.sht33_humid)
          break
    except Exception as e:
      num_consecutive_fails += 1
      print(f"A sensor read has failed {num_consecutive_fails} times due to {e}, trying again in 3 sec")
      time.sleep(3)

  #store data in sqlite and restart count
  if len(floor_temp_list) > 14:
    #sqlite command
    table = "long_term_data(date_time, ds18b20_floor, sht33_wall_temp, sht33_wall_humid)"
    data = (unix_timestamp, get_average(floor_temp_list), get_average(wall_temp_list), get_average(wall_humidity_list))  

    storage_functions.insert_into_table(table, data)
    print("stored some readings")
  

  #keep logging
  print("checked temp and now sleeping for 60 sec")
  time.sleep(60)

if __name__ == "__main__":
   pass