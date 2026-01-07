import sqlite3
from datetime import datetime

db = sqlite3.connect("/home/mads/Documents/Temp_logging_project/sensor_database.db")
cursor = db.cursor()

command = f"""
ALTER TABLE long_term_data RENAME TO old_db_structure_deprecated
"""

cursor.execute(command)

db.commit()
db.close()
