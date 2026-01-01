from sensor_analytics import analytics
from sensor_controller import registry
import time
import config

for i in range(15):
    data = registry.get_all_sensor_data()
    analytics.add_reading(data)

print(analytics.fetch_live_data())