import sqlite3

db = sqlite3.connect("/home/mads/Documents/Temp_logging_project/sensor_database.db")
cursor = db.cursor()

grab_command2 = f"""
INSERT INTO daily_aggregate (id, date, numReadings, aggregate, mean, weighted_sum, max, max_ts, min, min_ts)
VALUES ('head_height_desk_humidity', '2026-01-07', 96, 3262.3129000000013, 27.99, 1487.86534, 44.9, 1767788830, 27.99, 1767745929)
ON CONFLICT(id, date) 
DO UPDATE SET
    numReadings = excluded.numReadings,
    aggregate = excluded.aggregate,
    mean = excluded.mean,
    weighted_sum = excluded.weighted_sum,
    max = excluded.max,
    max_ts = excluded.max_ts,
    min = excluded.min,
    min_ts = excluded.min_ts;
"""

cursor.execute(grab_command2)
db.commit()

db.close()
