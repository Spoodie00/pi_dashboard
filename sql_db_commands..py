import sqlite3

db = sqlite3.connect("logging_data.db")
cursor = db.cursor()

command = """
ALTER TABLE dailyAggregateTable RENAME TO dailyAggregate
"""

cursor.execute(command)
db.commit()
cursor.close()