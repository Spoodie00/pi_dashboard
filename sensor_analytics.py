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
            self.averages[alias] = round(average, 4)

    def compute_extremes(self):
        date_today = datetime.now()
        now = int(date_today.timestamp())

        for alias, reading in self.averages.items():
            try:
                dict_max = self.extremes[alias]["max"]
                dict_min = self.extremes[alias]["min"]
            except KeyError:
                self.extremes[alias] = {}
                dict_max = 0
                dict_min = 100

            if reading > dict_max:
                self.extremes[alias]["max"] = reading
                self.extremes[alias]["max_ts"] = now
            
            if reading < dict_min:
                self.extremes[alias]["min"] = reading
                self.extremes[alias]["min_ts"] = now                
    
    def update_stddev_data_from_db(self, date):
        stddev_db_data = ()
        db_args = ["mean", "weighted_sum", "numReadings"]
        db_table = "daily_aggregate"

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
            print(f"For: {element[0]}")
            print(f"Mean: {mean}")
            print(f"Weighted sum: {weighted_sum}")
            print(f"Num readings: {numReadings} \n")

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
            avg = round(avg, 4)
            output.append((alias, date, avg))
        return output
        
    def fetch_daily_aggregate(self, date):
        output = []
        self.compute_averages()
        self.compute_extremes()
        self.update_running_stddev_data()

        for alias, readings in self.readings.items():
            aggregate = self.averages[alias]
            minval = self.extremes[alias]["min"]
            minval_ts = self.extremes[alias]["min_ts"]
            maxval = self.extremes[alias]["max"]
            maxval_ts = self.extremes[alias]["max_ts"]
            mean = self.stddev_data[alias]["mean"]
            wsum = self.stddev_data[alias]["weighted_sum"]
            num_reads = 1
            output.append((alias, date, num_reads, round(aggregate, 4), round(mean, 4), round(wsum, 4), maxval, maxval_ts, minval, minval_ts))
        return output
    
    def reset_readings(self):
        self.readings = {}
        self.num_readings = 0
        self.timestamps = []
    
    def daily_hard_reset(self):
        print(f"Less than {config.sensor_logger_cycle_sleep_time} seconds until midnight, pushed to db and sleeping until midnight has passed")
        self.averages = {}
        self.sums = {}
        self.extremes = {}
        self.stddev_data = {}
        sleep(30)
    
    def calculate_room_specific_heat_kwh(self, median_room_temp):
        median_room_temp_kelvin = median_room_temp + 273
        room_air_mass = config.room_air_volume*config.air_density
        room_specific_heat_kwh = (config.air_specific_heat_cap*room_air_mass*median_room_temp_kelvin)/3600
        return room_specific_heat_kwh

    def compute_room_stats(self, live_data_packet, adv_live_data):
        sensor_data = []
        for sensor in config.room_data_sensors:
            sens_dict = {"reading": live_data_packet[sensor["name"]]["reading"], "elevation": sensor["height"], "delta": adv_live_data[sensor["name"]]["hourly_delta"]}
            sensor_data.append(sens_dict)
        
        top_sensor_dict = max(sensor_data, key=lambda x: x["elevation"])
        top_sens_read = top_sensor_dict["reading"]
        top_sens_height = top_sensor_dict["elevation"]
        top_sens_delta = top_sensor_dict["delta"]

        bottom_sensor_dict = min(sensor_data, key=lambda x: x["elevation"])
        bottom_sens_read = bottom_sensor_dict["reading"]
        bottom_sens_height = bottom_sensor_dict["elevation"]
        bottom_sens_delta = bottom_sensor_dict["delta"]

        distance_between = top_sens_height - bottom_sens_height
        reading_delta = top_sens_read - bottom_sens_read
        degree_per_meter_up = reading_delta/(distance_between/100)

        roof_temp = top_sens_read + (((config.ceiling_height - top_sens_height)/100) * degree_per_meter_up)
        predicted_roof_temp = roof_temp + top_sens_delta
        if int(bottom_sens_height) != 0:
            floor_temp = bottom_sens_read - (bottom_sens_height * degree_per_meter_up)
        else:
            floor_temp = bottom_sens_read
        
        predicted_floor_temp = floor_temp + bottom_sens_delta

        median_room_temp = (floor_temp + roof_temp)/2
        actual_room_heat = self.calculate_room_specific_heat_kwh(median_room_temp)
        predicted_median_room_temp = (predicted_floor_temp + predicted_roof_temp)/2
        predicted_room_heat = self.calculate_room_specific_heat_kwh(predicted_median_room_temp)

        return {"avg_room_temp": round(median_room_temp, 2), "room_spec_heat": round(actual_room_heat*1000, 2), "room_energy_delta": round((predicted_room_heat - actual_room_heat)*1000, 2)}

analytics = Sensor_analytics()
