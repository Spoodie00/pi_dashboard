import sqlite3
from datetime import datetime

old_db = sqlite3.connect("/misc_database_files/old_db.db")
old_cursor = old_db.cursor()

new_db = sqlite3.connect("/misc_database_files/logging_data.db")
new_cursor = new_db.cursor()

grab_command = f"""
SELECT * 
FROM measurements
"""

old_cursor.execute(grab_command)
rows = old_cursor.fetchall()
old_db.close()
floor_temp_sum = 0
wall_temp_sum = 0
wall_humid_sum = 0
last_ts = 1732141692
stored_readings = 0
scrapped_readings = 0
sum_collapsed_readings = 0

def reset():
  global floor_temp_sum
  global wall_temp_sum
  global wall_humid_sum
  global stored_readings
  floor_temp_sum = 0
  wall_temp_sum = 0
  wall_humid_sum = 0
  stored_readings = 0

for row in rows:
  ts = row[1] + " " + row[2]
  dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S.%f")
  unix_ts = int(dt.timestamp())

  stored_readings += 1

  if (unix_ts - last_ts) > 70 or (unix_ts - last_ts) < 50:
    scrapped_readings += (stored_readings)
    reset()
    last_ts = unix_ts
    continue

  floor_temp_sum += round(float(row[3]), 2)
  wall_temp_sum += round(float(row[4]), 2)
  wall_humid_sum += round(float(row[5]), 2)

  last_ts = unix_ts

  if stored_readings == 15:
    ft = round((floor_temp_sum/15), 2)
    wt = round((wall_temp_sum/15), 2)
    wh = round((wall_humid_sum/15), 2)
    sum_collapsed_readings += stored_readings

    insert_command = f"""
    INSERT INTO long_term_data (date_time, ds18b20_floor, sht33_wall_temp, sht33_wall_humid)
    VALUES {last_ts, ft, wt, wh}
    """

    new_cursor.execute(insert_command)
    reset()

print("bad data")
print(scrapped_readings)
print("good data")
print(sum_collapsed_readings)
print("left over")
print(stored_readings)

new_db.commit()
new_db.close()
old_db.close()