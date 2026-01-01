from config import sensor_masterlist

class Sensor_registry:
    def __init__(self):
        self.sensors = {}
        self.auto_register_sensors()

    def auto_register_sensors(self):
        for name, params in sensor_masterlist.items():
            sensor_class = params["read_class"]
            instance = sensor_class(**params)
            self.sensors[instance.alias] = instance

    def get_all_sensor_data(self):
        reading_dict = {}
        for sensor_alias, sensor_object in registry.sensors.items():
            for reading_name, value in sensor_object.read().items():
                dict_key = f"{sensor_alias}_{reading_name}"
                reading_dict[dict_key] = round(value, 4)
        return reading_dict
    
    def get_sensor_object_by_alias(self, alias):
        return self.sensors[alias]

registry = Sensor_registry()
