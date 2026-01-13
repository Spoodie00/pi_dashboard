from sensor_controller import registry

sen = registry.get_sensor_object_by_alias("head_height_desk")

print(sen)
print(registry.get_sensor_parameters(sen))
