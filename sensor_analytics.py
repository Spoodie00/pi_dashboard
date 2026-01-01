import sqlite3
import config
from time import sleep
from datetime import datetime

class Sensor_analytics:
    def __init__(self):
        self.readings = {}
        self.averages = {}
        self.sums = {}
        self.extremes = {}
        self.stddev_data = {}
        self.timestamps = []
        self.num_readings = 0

    def add_reading(self, input: dict):
        for key, value in input.items():
            if key not in self.readings.keys():
                self.readings[key] = [value]
            else:
                self.readings[key].append(value)
        self.num_readings += 1
        date_today = datetime.now()
        now = int(date_today.timestamp())
        self.timestamps.append(now)
                        
    def compute_averages(self):
        self.averages = {}
        for alias, readings in self.readings.items():
            average = sum(readings)/len(readings)
            #output_key = f"{key}_avg"
            self.averages[alias] = round(average, 4)

    def compute_sums(self):
        self.sums = {}
        for alias, readings in self.readings.items():
            sensor_sum = sum(readings)
            #output_key = f"{key}_sum"
            self.sums[alias] = round(sensor_sum, 4)

    def compute_extremes(self):
        self.extremes= {}
        for alias, readings in self.readings.items():
            read_max = max(readings)
            read_min = min(readings)
            
            try:
                dict_max = self.extremes[alias]["max"]
                dict_min = self.extremes[alias]["min"]
            except KeyError:
                self.extremes[alias] = {}
                dict_max = 0
                dict_min = 100

            self.extremes[alias]["max"] = max(dict_max, read_max)
            self.extremes[alias]["min"] = min(dict_min, read_min)
    
    def update_stddev_data_from_db(self, date):
        stddev_db_data = ()
        db_args = ["mean", "weighted_sum", "numReadings"]
        db_table = "dailyAggregate"

        for attempt in range(5):
            try:
                connection = sqlite3.connect(config.database_directory)
                cursor = connection.cursor()
                command = f"""
                SELECT id, {db_args[0]}, {db_args[1]}, {db_args[2]} FROM {db_table} WHERE date = '{date}'
                """
                cursor.execute(command)
                stddev_db_data = cursor.fetchall()
                connection.close()
                break

            except Exception as e:
                print(f"Failed to grab existing stddev data {attempt} times due to {e}")
                sleep(2)
        
        if not stddev_db_data:
            print(f"Did not find any stddev data in {db_table} dated {date}, starting from scratch")
            return
        
        print(f"Found stddev data in {db_table} dated {date}, continuing said data")
        for element in stddev_db_data:
            mean = int(element[1])
            weighted_sum = int(element[2])
            numReadings = int(element[3])
            self.stddev_data[element[0]] = {db_args[0]: mean, db_args[1]: weighted_sum, db_args[2]: numReadings}

    def update_running_stddev_data(self):
        for alias, reading in self.averages.items():
            if alias in self.stddev_data.keys():
                mean = self.stddev_data[alias]["mean"]
                weighted_sum = self.stddev_data[alias]["weighted_sum"]
                num_readings = self.stddev_data[alias]["numReadings"]
            else:
                mean = 0
                weighted_sum = 0
                num_readings = 0

            old_mean = mean
            num_readings += 1

            mean += (reading-mean)/num_readings
            weighted_sum += (reading-mean)*(reading-old_mean)

            updated_stddev_dict = {"mean": mean, 
                                   "weighted_sum": weighted_sum,
                                   "numReadings": num_readings}
            self.stddev_data[alias] = updated_stddev_dict

    def get_temp_delta(self, sensors: list):
        readings = []
        for sensor in sensors:
            readings.append(self.averages[f"{sensor}_temps"])
        return abs(readings[0]-readings[1])
    
    def fetch_live_data(self):
        output = []
        for alias, readings in self.readings.items():
            for i in range(len(readings)):
                data_tuple = (alias, self.timestamps[i], readings[i])
                output.append(data_tuple)    
        return output
    
    def fetch_quarter_hour_average(self, date):
        output = []
        for alias, readings in self.readings.items():
            avg = sum(readings)/len(readings)
            output.append((alias, date, avg))
        return output

    
    def fetch_daily_aggregate(self, date):
        output = []
        self.compute_averages()
        self.compute_sums()
        self.compute_extremes()
        self.update_running_stddev_data()
        for alias, readings in self.readings.items():
            aggregate = self.sums[alias]
            minval = self.extremes[alias]["min"]
            maxval = self.extremes[alias]["max"]
            mean = self.stddev_data[alias]["mean"]
            wsum = self.stddev_data[alias]["weighted_sum"]
            num_reads = 1
            output.append((alias, date, num_reads, aggregate, mean, wsum, maxval, minval))
        return output
    
    def reset_readings(self):
        self.readings = {}
        self.num_readings = 0
        self.timestamps = []
    
    def daily_hard_reset(self):
        print(f"Less than {config.midnight_buffer_sec} seconds until midnight, pushed to db and sleeping until midnight has passed")
        self.averages = {}
        self.sums = {}
        self.extremes = {}
        self.stddev_data = {}
        sleep(config.midnight_buffer_sec + 10)

analytics = Sensor_analytics()


#analytics.update_stddev_data_from_db("2025-12-26")
#print(analytics.stddev_data)