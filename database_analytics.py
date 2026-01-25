import sqlite3
import config
import statistics
from itertools import islice
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
        self.avail_sensors = []
                
        for sensor in config.sensor_masterlist.values():
          for param in sensor["parameters"]:
            self.avail_sensors.append(f"{sensor["alias"]}_{param}")

    def get_past_unix_ts(self, **time_delta):
      iso8601_ts = datetime.now()
      iso8601_ts_24h_ago = iso8601_ts - timedelta(**time_delta)
      datetime_object = datetime.fromisoformat(str(iso8601_ts_24h_ago))
      past_unix_ts = int(datetime_object.timestamp())
      return past_unix_ts
    
    def build_sensor_clause(self, sensors: list):
        command = ""
        sensors_to_append = len(sensors)
        sensors_appended = 0
        
        for sensor in sensors:
          command += f"id = '{sensor}'"
          sensors_appended += 1

          if sensors_appended != sensors_to_append:
              command += "\nOR " 

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
        command += "\nAND ("
        command += built_clause
        command += ")"

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
    
    def HH_mm_since_ts(self, start_ts):
      end_ts = datetime.now().timestamp()
      duration = end_ts - start_ts
      hours = int(duration // 3600)
      minutes = int((duration % 3600) // 60)
      return f"{hours}h {minutes}m"

    
    def adv_live_data(self):
      readings = {}
      output = {}
      sensor_values = {}
      for sensor in self.avail_sensors:
        readings[sensor] = []
        output[sensor] = {}
        sensor_values[sensor] = []

      curr_time = datetime.now()
      midnight = datetime.combine(curr_time, datetime.min.time())
      midnight_time = int(midnight.timestamp())
      command = f"SELECT * FROM minute_data WHERE ts >= {midnight_time}"
      rows = self.fetchall(command)
      rows.reverse()
      for row in rows:
        id = row[0]
        ts = row[1]
        reading = row[2]
        readings[id].append((ts, reading))
        sensor_values[id].append(reading)

      for sensor in self.avail_sensors:
        dataset = readings[sensor]

        #Compute extremes
        it = iter(dataset)
        window_size = config.extremes_no_of_points_each_side*2      
        window = list(islice(it, window_size))
        output[sensor]["recent_local_max"] = None
        output[sensor]["recent_local_min"] = None

        for element in it:
          window += [element]

          window_vals = []
          for data_tuple in window:
            window_vals.append(data_tuple[1])

          center_tuple = window[config.extremes_no_of_points_each_side + 1]
          center_val = center_tuple[1]

          max_is_none = (output[sensor]["recent_local_max"] == None)
          window_max_is_centered = (max(window_vals) == center_val)
          if max_is_none and window_max_is_centered:
            dt_object = datetime.fromtimestamp(center_tuple[0])
            output[sensor]["recent_local_max"] = {"time": dt_object.strftime("%H:%M"), "timedelta": self.HH_mm_since_ts(center_tuple[0]), "val": round(center_tuple[1], 2)}
          
          min_is_none = (output[sensor]["recent_local_min"] == None)
          window_min_is_centered = (min(window_vals) == center_val)
          if min_is_none and window_min_is_centered:
            dt_object = datetime.fromtimestamp(center_tuple[0])
            output[sensor]["recent_local_min"] = {"time": dt_object.strftime("%H:%M"), "timedelta": self.HH_mm_since_ts(center_tuple[0]), "val": round(center_tuple[1], 2)}

          if not min_is_none and not max_is_none:
            break

          window = window[1:] + [element]

        #Compute rate of change
        hourly_delta_tuples = dataset[:5]
        hourly_delta_readings = []
        for read_tuple in hourly_delta_tuples:
          hourly_delta_readings.append(read_tuple[1])

        hourly_delta_val = (dataset[0][1] - (sum(hourly_delta_readings)/len(hourly_delta_readings)))*12
        output[sensor]["hourly_delta"] = round(hourly_delta_val, 2)

        #Compute trend
        if hourly_delta_val > config.sensor_rising_threshold:
          output[sensor]["trend"] = "Rising"
        elif hourly_delta_val < -config.sensor_sinking_threshold:
          output[sensor]["trend"] = "Sinking"
        else:
          output[sensor]["trend"] = "Stable"

        #Compute stability score
        output[sensor]["stability_score"] = round(1/(statistics.stdev(sensor_values[sensor])), 2)

        #Compute hours above target val
        sliced_sensor_string = sensor.rsplit("_", 1)
        sensor_object = registry.get_sensor_object_by_alias(sliced_sensor_string[0])
        target_val = registry.get_sensor_target_val(sensor_object, sliced_sensor_string[1])
        min_above_target = 0
        for reading in sensor_values[sensor]:
          if reading > target_val:
            min_above_target += 1
        hours = int(min_above_target // 60)
        minutes = int(min_above_target % 60)
        output[sensor]["time_above_target"] = f"{hours}h {minutes}m"

        #Add params from config
        param_dict = registry.build_sensor_params_dict(self.avail_sensors)
        output[sensor].update(param_dict[sensor])
        del output[sensor]["read_class"]
      return output
      


fetch_from_db = db_fetcher()