import sqlite3
from datetime import datetime

db = sqlite3.connect("/home/mads/Documents/Temp_logging_project/sensor_database.db")
cursor = db.cursor()

old_db = sqlite3.connect("/home/mads/Documents/Temp_logging_project/misc_database_files/logging_data_pre_new_schema.db")
old_cursor = old_db.cursor()

grab_command = f"""
SELECT * 
FROM long_term_data
WHERE date_time > 1767740399
"""

old_cursor.execute(grab_command)
rows = old_cursor.fetchall()

grab_command2 = f"""
SELECT * 
FROM daily_aggregate
WHERE date = '2026-01-07'"""

cursor.execute(grab_command2)
rows2 = cursor.fetchall()

old_db.close()

template = {"date": 0, "numreads": 0, "aggregate": 0, "mean": 0, "weighted_sum": 0, "max": 0, "max_ts": 0, "min": 100, "min_ts": 0}

output = {"floor_desk_temperature": {"date": rows2[0][1], "numreads": rows2[0][2], "aggregate": rows2[0][3], "mean": rows2[0][4], "weighted_sum": rows2[0][5], "max": rows2[0][6], "max_ts": rows2[0][7], "min": rows2[0][8], "min_ts": rows2[0][9]}, "head_height_desk_temperature": {"date": rows2[1][1], "numreads": rows2[1][2], "aggregate": rows2[1][3], "mean": rows2[1][4], "weighted_sum": rows2[1][5], "max": rows2[1][6], "max_ts": rows2[1][7], "min": rows2[1][8], "min_ts": rows2[1][9]}, "head_height_desk_humidity": {"date": rows2[2][1], "numreads": rows2[2][2], "aggregate": rows2[2][3], "mean": rows2[2][4], "weighted_sum": rows2[2][5], "max": rows2[2][6], "max_ts": rows2[2][7], "min": rows2[2][8], "min_ts": rows2[2][9]}}

outputls = []

for row in rows:
  tempdict = {"floor_desk_temperature": row[1], "head_height_desk_temperature": row[2], "head_height_desk_humidity": row[3]}
  for key, value in output.items():
    raw_ts = row[0]
    ts = datetime.fromtimestamp(raw_ts).date().isoformat()
    reading = tempdict[key]

    if value["date"] == 0:
      value["date"] = ts

    value["date"] = ts
    value["numreads"] += 1
    value["aggregate"] += reading

    oldmean = value["mean"]
    n = value["numreads"]
    value["mean"] += (reading-value["mean"])/n
    value["weighted_sum"] += (reading-value["mean"])*(reading-oldmean)

    if reading > value["max"]:
      value["max"] = reading
      value["max_ts"] = row[0]

    if reading < value["min"]:
      value["min"] = reading
      value["min_ts"] = row[0]

    if value["numreads"] == 96:
      name = key
      date = value["date"]
      nr = value["numreads"]
      agg = value["aggregate"] 
      mn = value["mean"]
      ws = round(value["weighted_sum"], 5)
      mx = value["max"]
      mxt = value["max_ts"]
      mn = value["min"]
      mnt = value["min_ts"]
      nre = 0

      outputls.append((name, date, nr, agg, mn, ws, mx, mxt, mn, mnt))
      output[key] = {"date": 0, "numreads": 0, "aggregate": 0, "mean": 0, "weighted_sum": 0, "max": 0, "max_ts": 0, "min": 100, "min_ts": 0}

#cursor.executemany(f"""INSERT INTO daily_aggregate (id, date, numReadings, aggregate, mean, weighted_sum, max, max_ts, min, min_ts) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", outputls)


print(outputls)

#db.commit()
db.close()
#cursor.execute(f""" DELETE FROM quarter_hour_data WHERE ts < {week_ago_iso}""") 
