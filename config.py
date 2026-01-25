from drivers import Read_ds18b20, Read_sht3x

database_directory = "/home/mads/Documents/Temp_logging_project/sensor_database.db"
min_num_readings = 15
sensor_logger_cycle_sleep_time = 60
midnight_buffer_sec = 100
roof_floor_delta_sensors = ["floor_desk", "head_height_desk"]

ceiling_height = 250 #cm
room_air_volume = 25.57696 #m3   empty = 26.875  standard = 25.57696 (kommode = 0.23104, seng = 1.044, skap = 1.176, annet = 1.024)
air_density = 1.2250 #kg/m3
air_specific_heat_cap = 1.007 #kJ/(kg*K)

room_data_sensors = [{"name": "floor_desk_temperature", "height": 0}, {"name": "head_height_desk_temperature", "height": 200}]
units = {"temperature": "°C", "humidity": "%"}
datalogger_filename = "datalogger.py"

#Live data params
sensor_rising_threshold = 1
sensor_sinking_threshold = 1
extremes_no_of_points_each_side = 50
extremes_local_threshold = 0.5

#Masterlist of all sensors and their properties, all other scripts pull from this list when dealing with sensors directly

sensor_masterlist = {
    "sensor 1": {
        "read_class": Read_ds18b20,
        "parameters": ["temperature"],
        "colors": {"temperature": "#101286"},
        "hardware_name": "ds18b20",
        "address": "28-3cb7e3819e17",
        "alias": "floor_desk",
        "display_name": "Floor",
        "info": "A temperature probe",
        "target_vals": {"temperature": 17},
        "units": {"temperature": "°C"}
    },
        
    "sensor 2": {
        "read_class": Read_sht3x,
        "parameters": ["temperature", "humidity"],
        "colors": {"temperature": '#fcba03', "humidity": "#860000"},
        "address": 0x45,
        "hardware_name": "SHT 30",
        "alias": "head_height_desk",
        "display_name": "Head height",
        "info": "A temperature and humidity board",
        "target_vals": {"temperature": 21, "humidity": 25},
        "units": {"temperature": "°C", "humidity": "%"}
    }
}