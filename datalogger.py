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

#directory = "/home/mads/Documents/Temp_logging_project/logging_data_copy_copy.db"
directory = "C:/Users/mads/Documents/pi_dashboard/logging_data_copy_copy.db"
list_of_sensors = ("ds18b20_floor_temp", "sht33_temp_wall", "sht33_humid_wall")

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
test_list = []

date_today = datetime.now()
date_today_iso = date_today.date().isoformat()

for attempt in range(3):
  try:
    connection = sqlite3.connect(directory)
    cursor = connection.cursor()
    command = f"""
    SELECT id, mean, weighted_sum, num_reads FROM dailyAggregate WHERE date = {date_today_iso}
    """
    results = cursor.fetchall()
  except Exception as e:
    print(f"Failed to grab existing stddev data due to {e}")
    
  stddev_db_data = {}
  if results:
    print("Found existing stddev data in db from today")
    for result in results:
       stddev_db_data[result[0]] = result[0:]
  else:
    for sensor in list_of_sensors:
       stddev_db_data[sensor] = (0, 0, 0)

start_time = time.time()
while True:
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
  min_delta_floor_wall = abs(min(min_delta_floor_wall, delta_floor_wall))

  live_data_values = (("ds18b20_floor_temp", prettify_value(ds18b20_floor_temp)), ("sht33_wall_temp", prettify_value(sht33_wall_temp)), ("sht33_wall_humid", prettify_value(sht33_wall_humid)))
  for sensor, value in live_data_values:
      live_data.append((sensor, now, value))

  num_readings += 1
  print(f"Number of lines logged: {num_readings} out of {minimum_number_of_readings}")

  #Push to db if its less than a minute until midnight
  date_post_midnight_buffer = date_today + timedelta(seconds=midnight_buffer_sec)
  date_post_midnight_buffer_iso = date_post_midnight_buffer.date().isoformat()

  if num_readings >= minimum_number_of_readings or date_post_midnight_buffer_iso != date_today_iso:
      connection = sqlite3.connect(directory)
      cursor = connection.cursor()

      cursor.execute("BEGIN;")

      cursor.executemany(f"""
                INSERT INTO liveData (id, ts, reading) 
                VALUES (?, ?, ?)
                """, live_data)
      
      sensor_values = [
        ("ds18b20_floor_temp", floor_temps),
        ("sht33_temp_wall", wall_temps),
        ("sht33_humid_wall", wall_humidities),
        ]   
      
      for sensor, values in sensor_values:

        #compute stddev data
        welford_new_value = sum(values)/len(values)

        welford_data = stddev_db_data[sensor]
        welford_mean = welford_data[0]
        welford_weighted_sum = welford_data[1]
        welford_num_reads = welford_data[2]

        welford_num_reads += 1
        welford_old_mean = welford_mean
        welford_mean += (welford_new_value - welford_mean)/welford_num_reads
        welford_weighted_sum += (welford_new_value - welford_mean)*(welford_new_value - welford_old_mean)

        welford_data = (welford_mean, welford_weighted_sum, welford_num_reads)
        stddev_db_data[sensor] = welford_data

        db_id = sensor
        db_date = date_today_iso
        db_numReadings = 1
        db_aggregate = sum(values)/len(values)
        db_mean = welford_mean
        db_weighted_sum = welford_weighted_sum
        db_maxDelta = round(max_delta_floor_wall, 2)
        db_minDelta = round(min_delta_floor_wall, 2)
        db_average = get_average(values)
        db_unix = now

        daily_aggregate = (db_id, db_date, db_numReadings, db_aggregate, db_mean, db_weighted_sum, db_maxDelta, db_minDelta)
        cursor.execute(f"""
                      INSERT INTO dailyAggregate (id, date, numReadings, aggregate, mean, weighted_sum, maxDelta, minDelta) 
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                      ON CONFLICT(id, date) DO UPDATE SET
                      numReadings = numReadings + excluded.numReadings,
                      aggregate = aggregate + excluded.aggregate,
                      mean = excluded.mean,
                      weighted_sum = excluded.weighted_sum,
                      maxDelta = MAX(maxDelta, excluded.maxDelta),
                      minDelta = MAX(minDelta, excluded.minDelta); 
                      """, daily_aggregate)
        
        quarter_hour_average = (db_id, db_unix, db_average)
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
      start_time = time.time()

      num_readings = 0
      floor_temps = []
      wall_temps = []
      wall_humidities = []
      live_data = []
      start_time = time.time()

      if date_post_midnight_buffer_iso != date_today_iso:
        print(f"Less than {midnight_buffer_sec} seconds until midnight, pushed to db and sleeping until midnight has passed")
        for sensor in list_of_sensors:
          stddev_db_data[sensor] = (0, 0, 0)
        time.sleep(midnight_buffer_sec)

if __name__ == "__main__":
   pass