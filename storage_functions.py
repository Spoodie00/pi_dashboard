import sqlite3
from datetime import datetime
import config
import json

def to_unix(date):
  pattern = f"%Y-%m-%dT%H:%M"
  ts = int(datetime.strptime(date, pattern).timestamp())
  return ts

def collect_all_data(start_date, end_date=None):
  unix_start = to_unix(start_date)

  print(unix_start)

  command = f"""
  SELECT * 
  FROM long_term_data 
  WHERE date_time > {unix_start}
  """
  if end_date:
    unix_ts_stop = to_unix(end_date)
    command = command + f"AND date_time < {unix_ts_stop}"

  connection = sqlite3.connect(config.database_directory)
  cursor = connection.cursor()
  cursor.execute("BEGIN")
  cursor.execute(command)
  rows = cursor.fetchall()
  connection.close()

  output = {"labels": [], "ds18b20": [], "sht33t": [], "sht33h": []}

  for row in rows:
    unix_ts = row[0]
    iso_ts = datetime.fromtimestamp(unix_ts).isoformat()
    output["labels"].append(iso_ts)
    output["ds18b20"].append(row[1])
    output["sht33t"].append(row[2])
    output["sht33h"].append(row[3])

  return json.dumps(output)

def fetch_raw_db_data(columns, table, clause, extra=None):
  connection = sqlite3.connect('/home/mads/Documents/Temp_logging_project/logging_data.db')
  cursor = connection.cursor()
  
  command = f"""
  SELECT {columns} 
  FROM {table}
  {clause}
  """

  if extra is not None:
    command += extra

  cursor.execute(command)
  rows = cursor.fetchall()
  connection.close()
  
  return rows

def unix_to_readable_date(ts):
  return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')

def get_extremes_data(table_names, start_date_list):
  data_dict = {}

  for name in table_names:
    for date in start_date_list:
      columns_max = f"{name}_max, {name}_max_ts"
      columns_min = f"{name}_min, {name}_min_ts"
      table = f"daily_stats_{name}"
      clause = f"WHERE date >= '{date}'"
      order_max = f"""ORDER BY {name}_max DESC
                LIMIT 1"""
      order_min = f"""ORDER BY {name}_min ASC
                LIMIT 1"""
      
      data_max = fetch_raw_db_data(columns_max, table, clause, order_max)
      data_min = fetch_raw_db_data(columns_min, table, clause, order_min)

      data_dict[f"{name}_max_{date}"] = data_max[0][0]
      data_dict[f"{name}_max_ts_{date}"] = unix_to_readable_date(data_max[0][1])
      data_dict[f"{name}_min_{date}"] = data_min[0][0]
      data_dict[f"{name}_min_ts_{date}"] = unix_to_readable_date(data_min[0][1])

  return data_dict

if __name__ == "__main__":
  import statistics
  import math
  whole = [3, 4, 5, 2, 9, 10, 2, 7, 1, 3, 6]
  new_mean = 0
  sum_of_weights = 0
  n = 0

  for reading in whole:
    n += 1
    old_mean = new_mean
    new_mean += (reading - new_mean)/n
    sum_of_weights += (reading - new_mean)*(reading - old_mean)
    print(sum_of_weights)

  print(math.sqrt(sum_of_weights/(n-1)))
  print(statistics.stdev(whole))