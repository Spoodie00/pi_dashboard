import sqlite3
from datetime import datetime

db = sqlite3.connect("/home/mads/Documents/Temp_logging_project/misc_database_files/logging_data_copy_copy.db")
cursor = db.cursor()

command = f"""
SELECT * FROM quarter_hour_data
"""

cursor.execute(command)
rows = cursor.fetchall()

db.commit()
db.close()

print(rows)
