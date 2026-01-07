import sensors
import time
import sqlite3
import config
from sensor_analytics import analytics
from sensor_controller import registry
from datetime import datetime, timedelta
  
start_time = time.time()
while True:
  data = registry.get_all_sensor_data()
  analytics.add_reading(data)
  print(f"Number of lines logged: {analytics.num_readings} out of {config.min_num_readings}, sleeping for {config.sensor_logger_cycle_sleep_time} seconds")

  #Push to db if its less than a minute until midnight
  date_today = datetime.now()
  date_today_iso = date_today.date().isoformat()
  date_post_midnight_buffer = date_today + timedelta(seconds=config.midnight_buffer_sec)
  date_post_midnight_buffer_iso = date_post_midnight_buffer.date().isoformat()

  if analytics.num_readings >= config.min_num_readings or date_post_midnight_buffer_iso != date_today_iso:
      now = int(time.time())
      day_ago = date_today - timedelta(days=1)
      day_ago_iso = day_ago.date().isoformat()
      week_ago = date_today - timedelta(days=7)
      week_ago_iso = week_ago.date().isoformat()

      connection = sqlite3.connect(config.database_directory)
      cursor = connection.cursor()

      cursor.execute("BEGIN;")

      live_data = analytics.fetch_live_data()
      cursor.executemany(f"""
                INSERT INTO minute_data (id, ts, reading) 
                VALUES (?, ?, ?)
                """, live_data)

      daily_aggregate = analytics.fetch_daily_aggregate(date_today_iso)
      cursor.executemany(f"""
                    INSERT INTO daily_aggregate (id, date, numReadings, aggregate, mean, weighted_sum, max, max_ts, min, min_ts) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id, date) DO UPDATE SET
                    numReadings = numReadings + excluded.numReadings,
                    aggregate = aggregate + excluded.aggregate,
                    mean = excluded.mean,
                    weighted_sum = excluded.weighted_sum,
                    max = excluded.max,
                    max_ts = excluded.max_ts,
                    min = excluded.min,
                    min_ts = excluded.min_ts; 
                    """, daily_aggregate)
      
      quarter_hour_average= analytics.fetch_quarter_hour_average(now)
      cursor.executemany(f"""
                    INSERT INTO quarter_hour_data (id, ts, reading)
                    VALUES (?, ?, ?)
                    """, quarter_hour_average)
      
      cursor.execute(f"""
                    DELETE FROM minute_data 
                    WHERE ts < {day_ago_iso}
                    """)       
      
      cursor.execute(f"""
                    DELETE FROM quarter_hour_data 
                    WHERE ts < {week_ago_iso}
                    """) 

      cursor.executemany(f"""
                    INSERT INTO master_table (id, ts, reading)
                    VALUES (?, ?, ?)
                    """, quarter_hour_average)

      connection.commit()
      connection.close()
      print(f"Pushed to database, total time since last push: desired = {(config.min_num_readings - 1)*config.sensor_logger_cycle_sleep_time}, actual = {time.time() - start_time}")
      start_time = time.time()
      analytics.reset_readings()
      
      if date_post_midnight_buffer_iso != date_today_iso:
        analytics.daily_hard_reset()
    
  time.sleep(config.sensor_logger_cycle_sleep_time)

if __name__ == "__main__":
   pass