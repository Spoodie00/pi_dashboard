import sqlite3
from datetime import datetime

connection = sqlite3.connect('/home/spoodie/Documents/Temp_logging_project/logging_data.db')
cursor = connection.cursor()

def daily_stats_table_ds18b20_1():
    command = f"""
    CREATE TABLE daily_stats_ds18b20_1 (
        date REAL PRIMARY KEY,
        read_count INTEGER,
        ds18b20_1_max REAL,
        ds18b20_1_max_ts REAL,
        ds18b20_1_min REAL,
        ds18b20_1_min_ts REAL,        
        ds18b20_1_sum_x REAL,
        ds18b20_1_sum_x2 REAL    
    );
    """
    cursor.execute(command)
    connection.close()
    print("executed command")

def trigger_creator(tag, name):
    command = f"""
    CREATE TRIGGER trg_daily_stats_{tag}
    AFTER INSERT ON long_term_data
    BEGIN
        INSERT INTO daily_stats_{tag}(date, read_count, {tag}_max, {tag}_max_ts, {tag}_min, {tag}_min_ts, {tag}_sum_x, {tag}_sum_x2)

        VALUES(date(NEW.date_time, 'unixepoch'), 1, NEW.{name}, NEW.date_time, NEW.{name}, NEW.date_time, NEW.{name}, NEW.{name})

        ON CONFLICT(date) DO UPDATE SET
        read_count = read_count + 1,
        {tag}_max = MAX({tag}_max, NEW.{name}),
        {tag}_max_ts = CASE 
            WHEN NEW.{name} > {tag}_max
            THEN NEW.date_time
            ELSE {tag}_max_ts END,
    
        {tag}_min = MIN({tag}_min, NEW.{name}),
        {tag}_min_ts = CASE 
            WHEN NEW.{name} < {tag}_min
            THEN NEW.date_time
            ELSE {tag}_min_ts END,
        
        {tag}_sum_x = ROUND({tag}_sum_x + NEW.{name}, 2),
        {tag}_sum_x2 = ROUND({tag}_sum_x2 + NEW.{name}*NEW.{name}, 2);
    END;
    """
    cursor.execute(command)
    connection.close()
    print("executed command")

def see_all_tables(tag):
    command = f"""
    SELECT name FROM sqlite_master WHERE type='{tag}';
    """
    cursor.execute(command)
    print(cursor.fetchall())
    connection.close()

def drop_table(table):
    command = f"""
    DROP TABLE {table}
    """
    cursor.execute(command)
    connection.close()
    print("dropped table")

def general_command():
    command = f'''
    ALTER TABLE daily_stats_sht33_1_temp
    RENAME COLUMN sht33_1_sum_x2 TO sht33_1_temp_sum_x2
    '''
    cursor.execute(command)
    connection.close()
    print("commanded table")

def unix_to_readable_date(ts):
  return datetime.fromtimestamp(ts).strftime('%Y-%m-%d')

def store_restored(current_date, n, max_read, max_read_ts, min_read, min_read_ts, sum_x, sum_x2):
    connection = sqlite3.connect('/home/spoodie/Documents/Temp_logging_project/logging_data.db')
    cursor = connection.cursor()
    command = f"""
    INSERT INTO daily_stats_sht33_1_temp
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """

    cursor.execute(command, (current_date, n, max_read, max_read_ts, min_read, min_read_ts, round(sum_x, 2), round(sum_x2, 2)))

    connection.commit()
    connection.close()


def restore_data():
    connection = sqlite3.connect('/home/spoodie/Documents/Temp_logging_project/logging_data.db')
    cursor = connection.cursor()
    command = f"""
    SELECT date_time, sht33_wall_temp FROM long_term_data WHERE date_time > 1
    """
    cursor.execute(command)
    data = cursor.fetchall()
    connection.close()

    current_date = 0

    max_read = 0
    max_read_ts = 0
    min_read = 1000
    min_read_ts = 0
    sum_x = 0
    sum_x2 = 0
    n = 0

    for reading in data:
        read_date = unix_to_readable_date(reading[0])

        if current_date != 0 and read_date != current_date:
            store_restored(current_date, n, max_read, max_read_ts, min_read, min_read_ts, sum_x, sum_x2)
            max_read = 0
            max_read_ts = 0
            min_read = 1000
            min_read_ts = 0
            sum_x = 0
            sum_x2 = 0
            n = 0
        
        current_date = read_date
    
        if reading[1] > max_read:
            max_read = reading[1]
            max_read_ts = reading[0]

        if reading[1] < min_read:
            min_read = reading[1]
            min_read_ts = reading[0]
        
        sum_x += reading[1]
        sum_x2 += reading[1]**2
        n += 1

    print("restored")

    store_restored(current_date, n, max_read, max_read_ts, min_read, min_read_ts, sum_x, sum_x2)

def delete_data():
    connection = sqlite3.connect('/home/spoodie/Documents/Temp_logging_project/logging_data.db')
    cursor = connection.cursor()
    command = f"""
    DELETE FROM daily_stats_sht33_1_temp WHERE read_count > 0
    """

    cursor.execute(command)

    connection.commit()
    connection.close()

if __name__ == "__main__":
    delete_data()    
    restore_data()


"""
daily_stats_table_structure:
    date REAL PRIMARY KEY,
    read_count INTEGER,
    ds18b20_1_max REAL,
    ds18b20_1_max_ts REAL,
    ds18b20_1_min REAL,
    ds18b20_1_min_ts REAL,        
    ds18b20_1_sum_x REAL,
    ds18b20_1_sum_x2 REAL   
"""
