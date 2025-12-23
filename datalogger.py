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

minimum_number_of_readings = 15
midnight_buffer_sec = 60

floor_temps = []
wall_temps = []
wall_humidities = []
live_data = []
delay = 2

date_today = datetime.now()
date_today_iso = date_today.date().isoformat()

for attempt in range(3):
  try:
    connection = sqlite3.connect('/home/mads/Documents/Temp_logging_project/logging_data_copy.db')
    cursor = connection.cursor()
    command = f"""
    SELECT mean, sum, num_reads FROM dailyAggregate WHERE date = {date_today_iso}
    """
    result = cursor.fetchone()
  except Exception as e:
    print(f"failed to grab existing stddev data due to {e}")

if result:
  readings_today, mean_today, sum_today = result[0]
else:
  readings_today = 0
  mean_today = 0
  sum_today = 0

while True:
  start_time = time.time()
  time.sleep(delay)

  max_consecutive_fails = 5

  for attempt in range(max_consecutive_fails + 1):
    try:
          ds18b20_floor_temp = sensors.get_ds18b20_temp("28-3cb7e3819e17")
          sht33_wall_temp = sensors.sht33_temp()
          sht33_wall_humid = sensors.sht33_humid()
          break
    
    except Exception as e:
      num_consecutive_fails -= 1
      print(f"A sensor read has failed {5-num_consecutive_fails} times due to {e}, trying again in 3 sec")
      if num_consecutive_fails == 0:
         continue
      time.sleep(3)

  date_today = datetime.now()
  date_today_iso = date_today.date().isoformat()

  now = int(date_today.timestamp())

  floor_temps.append(ds18b20_floor_temp)
  wall_temps.append(sht33_wall_temp)
  wall_humidities.append(sht33_wall_humid)

  delta_floor_wall = abs(ds18b20_floor_temp - sht33_wall_temp)
  max_delta_floor_wall = max(max_delta_floor_wall, delta_floor_wall)
  min_delta_floor_wall = max(min_delta_floor_wall, delta_floor_wall)

  readings_today += 1
  old_mean_today = mean_today
  mean_today = mean_today + 0

  live_data_values = (("ds18b20_floor_temp", prettify_value(ds18b20_floor_temp)), ("sht33_wall_temp", prettify_value(sht33_wall_temp)), ("sht33_wall_humid", prettify_value(sht33_wall_humid)))

  for sensor, value in live_data_values:
      live_data.append((now, sensor, value))

  num_readings += 1
  print(f"Number of lines logged: {num_readings} out of {minimum_number_of_readings}")

  #Push to db if its less than a minute until midnight
  date_post_midnight_buffer = date_today + timedelta(seconds=midnight_buffer_sec)
  date_post_midnight_buffer_iso = date_post_midnight_buffer.date().isoformat()

  if num_readings >= minimum_number_of_readings or date_post_midnight_buffer_iso != date_today:
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
        db_aggregate = round(sum(values), 2)
        db_variance = round(statistics.variance(values), 2)
        db_maxDelta = round(max_delta_floor_wall, 2)
        db_minDelta = round(min_delta_floor_wall, 2)
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
      
      day_ago = date_today - timedelta(days=1)
      day_ago_iso = day_ago.date().isoformat()
      cursor.execute(f"""
                    DELETE FROM liveData 
                    WHERE ts < {day_ago_iso}
                    """)       
      
      week_ago = date_today - timedelta(days=7)
      week_ago_iso = week_ago.date().isoformat()
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
      print(f"Pushed to database, total time since last push: desired = {num_readings*delay}, actual = {time.time() - start_time}")

      num_readings = 0
      floor_temps = []
      wall_temps = []
      wall_humidities = []
      live_data = []
      start_time = time.time()

if __name__ == "__main__":
   pass