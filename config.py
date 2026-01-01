from drivers import Read_ds18b20, Read_sht3x

#directory = "/home/mads/Documents/Temp_logging_project/logging_data_copy_copy.db"
database_directory = "C:/Users/mads/Documents/pi_dashboard/logging_data_copy_copy.db"
min_num_readings = 15
sensor_logger_cycle_sleep_time = 2
midnight_buffer_sec = 60
roof_floor_delta_sensors = ["desk_floor", "desk_head_height"]

#Masterlist of all sensors and their properties, all other scripts pull from this list when dealing with sensors directly

sensor_masterlist = {
    "sensor 1": {
        "read_class": Read_ds18b20,
        "address": "28-3cb7e3819e17",
        "alias": "desk_floor",
        "info": "A temperature probe"
    },
        
    "sensor 2": {
        "read_class": Read_sht3x,
        "address": "0x45",
        "alias": "desk_head_height",
        "info": "A temperature and humidity board"
    }
}