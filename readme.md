<h1>TODO:</h1>

<h2>Live data:</h2>

- Some kind of "temperature rise last hour for mainpage samt grader per min/time
- Estimate energi in the system using volume of air
- Calculate data regarding room energy and try to estimate heat input/output into the system

<h2>Historical data:</h2>

- Heatmap last 30 days to visualize average temps for the period
- Heatmap of hour-by-hour average last x days?
- Column plot to visualize distro of avg temps during last 30 days

<h2>Misc:</h2>

- Expand stats page
- Degree hours in some way? (hours under x degrees within this period)
- Stability score a la "1/stdavg"
- Average data around wake-up and bedtime
- It is possible to estimate when i'm home or asleep?
- Correlation matrix
- ~~Merge old data~~
- Make debugger (start/stop measurements of specified sensor every x seconds and plot it)
- data_logger.py status indicator on live page
- Split temperature dashboard into a separate module and make a landing page which directs you to different modules
- Replay module (display new reading every x seconds within a specific historic time segment)
- Use average loop run time last x loops to adjust sleep time accordingly as to meet goal sleep time
- WiFi scanner and visualization tool
- Gmail or discord bot to check status when away
- ~~Need new naming scheme for sensors datalogger.py~~
- ~~Refactor datalogger.py for it to easier adapt to different and new sensors~~
- Refactor all code to better adhere to best practices and style guides
- Refactor storage_functions.py and rename it
- Refactor sensors.py
- Refactor app.py
- Refactor all JS scripts and HTML/CSS code.
- Merge old data to new DB data structure
- Log any change in sensor alias or position as to keep db working when moved

<h2>One day:</h2>

- Hourly average compared to normal average this time of night
- Separate main table into yearly main tables
- Weather forecast module
- External temp sensor on a separate board lying outside and connected using flask
- Wind measurements
- Add more sensors 
- Forecasted vs actual conditions
- Profile scripts to reduce compute effort where possible (Low granularity)
- Profile scripts to reduce compute effort where possible (High granularity)


<h2>New Modules:</h2>

- Politiloggen dashboard
  - Collect and store events nearby
  - Display on map
  - Send email to user when specific event category is logged

- Pantry storage system
  - sort by location/date/category
  - Stats regarding what i have eaten
  - Suggest meals using the ingredients i have in store
  - Image recognition to find expiration dates and whether its BB or use by

- Device monitor amd cyber stuff
  - CPU, RAM, disk stats
  - SD card health
  - Flask uptime
  - DB size growth
  - View error logs

- Weather module
  - Predict/list rain/snow during the day

<h2>Table plan:</h2>

- Main_storage (keeps every 15 min aggregate forever)
  - readings
  - ts

- live_stats (tracked every minute but pushed to db every 15, purged if older than 24 hours)
  - id
  - readings
  - ts
  - one row per sensor per 15 min

- quarterly-aggregate (15 min of data aggregated for each row, purged after a week, serves to offload main table)
  - id
  - readings
  - ts
  - one row per sensor per 15 min

- history (aggregate a day of data per line (pushed every 15 mins))
  - id
  - date
  - num_readings
  - aggregate
  - mean
  - weighted_sum
  - max_delta
  - min_delta
  - one line per sensor per day

- stats_table (cache of every key statistic requested by user, refreshed every 15 or 60 min, relieves stress on large tables)
