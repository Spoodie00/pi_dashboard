import sqlite3
import config
from datetime import datetime, timedelta
from sensor_controller import registry
from collections import defaultdict

class db_fetcher:
    def __init__(self):
        #Add a 30 second buffer to start times to ensure the correct query is executed
        self.ts_buffer = 30
        self.reading_bundle = 0
        self.ts_bundle = 0
        self.bundled_readings = 0

    def get_past_unix_ts(self, **time_delta):
      iso8601_ts = datetime.now()
      iso8601_ts_24h_ago = iso8601_ts - timedelta(**time_delta)
      datetime_object = datetime.fromisoformat(str(iso8601_ts_24h_ago))
      past_unix_ts = int(datetime_object.timestamp())
      return past_unix_ts
    
    def build_sensor_clause(self, sensors: list):
        command = "\nAND ("
        sensors_to_append = len(sensors)
        sensors_appended = 0
        
        for sensor in sensors:
          command += f"id = '{sensor}'"
          sensors_appended += 1

          if sensors_appended != sensors_to_append:
              command += "\nOR " 

        command += ")"
        return command
       
    def fetchall(self, command):
      db = sqlite3.connect(config.database_directory)
      cursor = db.cursor()
      cursor.execute(command)
      rows = cursor.fetchall()
      db.close()
      return rows
    
    def unix_to_full_iso(self, unix_ts):
      dt_obj = datetime.fromtimestamp(unix_ts)
      return dt_obj.strftime("%Y-%m-%d %H:%M")
    
    def unix_to_HHmm(self, unix_ts):
      dt_obj = datetime.fromtimestamp(unix_ts)
      return dt_obj.strftime('%H:%M')
    
    def unix_to_YYYY_MM_DD(self, unix_ts):
      dt_obj = datetime.fromtimestamp(unix_ts)
      return dt_obj.strftime('%Y-%m-%d')


    def graph_data(self, date, sample_rate, sensors: list=[]):
      unix_ts_start = self.get_past_unix_ts(hours=24*float(date))
      buffered_unix_ts_start = unix_ts_start + self.ts_buffer
      unix_ts_24h_ago = self.get_past_unix_ts(days=1)
      unix_ts_1w_ago = self.get_past_unix_ts(days=7)
      command = ""
      #How many rows to compress into a single datapoint, typically 3 for sub-24h and 1 for everything else

      if unix_ts_24h_ago < buffered_unix_ts_start:
        command = f"""SELECT * \nFROM minute_data \nWHERE ts >= {unix_ts_start}"""
        ts_handler = self.unix_to_HHmm
      elif unix_ts_24h_ago > buffered_unix_ts_start > unix_ts_1w_ago:
        command = f"""SELECT * \nFROM quarter_hour_data \nWHERE ts >= {unix_ts_start}"""
        ts_handler = self.unix_to_full_iso
      elif buffered_unix_ts_start < unix_ts_1w_ago:
        date_iso = self.unix_to_YYYY_MM_DD(unix_ts_start)
        command = f"""SELECT id, date, (aggregate / numReadings) \nFROM daily_aggregate \nWHERE date >= '{date_iso}'"""
        ts_handler = self.unix_to_YYYY_MM_DD
      
      if sensors:
        built_clause = self.build_sensor_clause(sensors)
        command += built_clause

      rows = self.fetchall(command)
      
      data_dict = defaultdict(lambda: {"values": [], "ts": [], "buffer": {"ts": [], "readings": []}})

      for id, ts, reading in rows:
        entry = data_dict[id]
        bufferdict = entry["buffer"]

        if isinstance(ts, int):
          bufferdict["ts"].append(ts)
        else:
          date_object = datetime.strptime(ts, '%Y-%m-%d')
          bufferdict["ts"].append(date_object.timestamp())

        bufferdict["readings"].append(reading)

        if len(bufferdict["readings"]) >= int(sample_rate):
          avg_ts = sum(bufferdict["ts"])/len(bufferdict["ts"])
          formatted_ts = ts_handler(avg_ts)
          entry["ts"].append(formatted_ts)

          avg_read = sum(bufferdict["readings"])/len(bufferdict["readings"])
          entry["values"].append(round(avg_read, 2))
    
          entry["buffer"] = {"ts": [], "readings": []}
     
      param_dict = registry.build_sensor_params_dict(sensors)
      for name, subdict in data_dict.items():
        data_dict[name] = subdict | param_dict[name]
        del data_dict[name]["buffer"] 
        del data_dict[name]["read_class"]
      return data_dict

fetch_from_db = db_fetcher()