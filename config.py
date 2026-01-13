from drivers import Read_ds18b20, Read_sht3x

database_directory = "/home/mads/Documents/Temp_logging_project/sensor_database.db"
min_num_readings = 15
sensor_logger_cycle_sleep_time = 60
midnight_buffer_sec = 100
roof_floor_delta_sensors = ["floor_desk", "head_height_desk"]
units = {"temperature": "°C", "humidity": "%"}

#Masterlist of all sensors and their properties, all other scripts pull from this list when dealing with sensors directly

sensor_masterlist = {
    "sensor 1": {
        "read_class": Read_ds18b20,
        "parameters": ["temperature"],
        "colors": {"temperature": "#101286"},
        "address": "28-3cb7e3819e17",
        "alias": "floor_desk",
        "display_name": "Floor",
        "info": "A temperature probe"
    },
        
    "sensor 2": {
        "read_class": Read_sht3x,
        "parameters": ["temperature", "humidity"],
        "colors": {"temperature": '#fcba03', "humidity": "#860000"},
        "address": 0x45,
        "alias": "head_height_desk",
        "display_name": "Head height",
        "info": "A temperature and humidity board"
    }
}