import sqlite3
from datetime import datetime

list = ["ds18b20_floor", "sht33_temp_wall", "sht33_humid_wall"]

db = sqlite3.connect("C:/Users/mads/Documents/pi_dashboard/logging_data_copy_copy.db")
cursor = db.cursor()

date_today_iso = datetime.now().date().isoformat()
command = f"""
ALTER TABLE dailyAggregate
RENAME COLUMN minDelta TO min
"""

del_list = ["DELETE FROM liveData", "DELETE FROM weekBuffer", "DELETE FROM dailyAggregate"]

[cursor.execute(del_command) for del_command in del_list]
#results = cursor.execute(command)
#cursor.execute(command)

db.commit()
db.close()
