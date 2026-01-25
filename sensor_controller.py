import config

class Sensor_registry:
    def __init__(self):
        self.sensors = {}
        self.auto_register_sensors()

    def auto_register_sensors(self):
        for name, params in config.sensor_masterlist.items():
            sensor_class = params["read_class"]
            instance = sensor_class(**params)
            self.sensors[instance.alias] = instance

    def get_all_sensor_data(self, pretty=False):
        reading_dict = {}
        for sensor_alias, sensor_object in self.sensors.items():
            for reading_name, value in sensor_object.read(sensor_object.address).items():
                dict_key = f"{sensor_alias}_{reading_name}"
                if pretty:
                    unit = sensor_object.units[reading_name]
                    reading_dict[dict_key] = {"reading": value, "unit": unit, "display_name": f"{sensor_object.display_name} {reading_name}"}
                else:
                    reading_dict[dict_key] = value
        return reading_dict
    
    def get_avaliable_sensors(self):
        output = {}
        for sens_name, sens_obj in self.sensors.items():
            for parameter in sens_obj.parameters:
                sensor_string = f"{sens_name}_{parameter}"
                display_name = f"{sens_obj.display_name} {parameter}"
                output[display_name] = sensor_string
        return output
    
    def build_sensor_params_dict(self, sensor_list):
        output = {}
        for placeholder, subdict in config.sensor_masterlist.items():
            for param in subdict["parameters"]:
                if f"{subdict["alias"]}_{param}" not in sensor_list:
                    continue

                altered_subdict = subdict.copy()
                altered_subdict["display_name"] = f"{subdict["display_name"]} {param}"
                altered_subdict["unit"] = altered_subdict["units"][param]
                altered_subdict["target_val"] = altered_subdict["target_vals"][param]
                if "colors" not in altered_subdict.keys():
                    altered_subdict["colors"] = {}

                del altered_subdict["parameters"]
                del altered_subdict["units"]
                del altered_subdict["target_vals"]
                output[f"{subdict["alias"]}_{param}"] = altered_subdict
        return output


    def get_sensor_object_by_alias(self, alias):
        return self.sensors[alias]
    
    def get_sensor_target_val(self, sens_obj, param):
        return sens_obj.target_vals[param]
    
    def get_sensor_parameters(self, sens_obj):
        return sens_obj.parameters
    
    def get_sensor_display_name(self, sens_obj):
        return "{sens_obj.display_name}_{}"
    
    def get_sensor_color(self, sens_obj, param):
        if not hasattr(sens_obj, "colors"):
            return None
        
        color_dict = sens_obj.colors
        if param not in color_dict.keys():
            return None
        
        return color_dict[param]

registry = Sensor_registry()

if __name__ == "__main__":
    registry.get_avaliable_sensors()