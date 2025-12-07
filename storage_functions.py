import sqlite3
from datetime import datetime

def insert_into_table(table_info, value_placeholder, data):
  connection = sqlite3.connect('/home/mads/Documents/Temp_logging_project/logging_data.db')
  cursor = connection.cursor()
  command = f"""
  INSERT INTO {table_info}
  VALUES {value_placeholder}
  """

  cursor.execute(command, data)

  connection.commit()
  connection.close()

def convert_custom_ts_to_unix(custom_ts):
  custom_ts = str(custom_ts)
  hours = int(custom_ts[0:2])
  minutes = int(custom_ts[2:4])
  day = int(custom_ts[4:6])
  month = int(custom_ts[6:8])
  year = int(custom_ts[8:12])

  if hours == 99:
    hours = 00
  
  dt = datetime(year, month, day, hours, minutes)

  return int(dt.timestamp())

def prettify_numbers(number):
    trailed_num = f"{number:.2f}"
    return trailed_num

def collect_data(start_time, end_time=0):
  connection = sqlite3.connect('/home/mads/Documents/Temp_logging_project/logging_data.db')
  cursor = connection.cursor()

  unix_ts_start = convert_custom_ts_to_unix(start_time)
  #unix_ts_start = 1747082270

  command = f"""
  SELECT * 
  FROM long_term_data 
  WHERE date_time > {unix_ts_start}
  """
  if end_time != 0:
    unix_ts_stop = convert_custom_ts_to_unix(end_time)
    command = command + f"AND date_time < {unix_ts_stop}"

  cursor.execute(command)
  rows = cursor.fetchall()
  connection.close()

  temp_ds18b20 = []
  temp_sht33 = []
  humid_sht33 = []
  labels = []

  for row in rows:
    readable = datetime.fromtimestamp(row[0]).strftime('%d. %B %H:%M')
    labels.append(readable)
    temp_ds18b20.append(prettify_numbers(row[1]))
    temp_sht33.append(prettify_numbers(row[2]))
    humid_sht33.append(prettify_numbers(row[3]))

  return labels, temp_ds18b20, temp_sht33, humid_sht33

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

      data_dict[f"{name}_max_{date}"] = prettify_numbers(data_max[0][0])
      data_dict[f"{name}_max_ts_{date}"] = unix_to_readable_date(data_max[0][1])
      data_dict[f"{name}_min_{date}"] = prettify_numbers(data_min[0][0])
      data_dict[f"{name}_min_ts_{date}"] = unix_to_readable_date(data_min[0][1])



  return data_dict

if __name__ == "__main__":
  print(get_extremes_data(["ds18b20_1"], ["2025-05-25"]))