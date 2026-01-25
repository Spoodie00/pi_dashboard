<h1>TODO:</h1>

<h2>Live data:</h2>

- Nothing

<h2>Historical data:</h2>

- Heatmap last 30 days to visualize average temps for the period
- Heatmap of hour-by-hour average last x days?
- Column plot to visualize distro of avg temps during last 30 days

<h2>Misc:</h2>

- Expand stats page
- Average data around wake-up and bedtime
- It is possible to estimate when im home or asleep?
- Correlation matrix
- Make debugger (start/stop measurements of specified sensor every x seconds and plot it)
- Split temperature dashboard into a separate module and make a landing page which directs you to different modules
- Replay module (display new reading every x seconds within a specific historic time segment)
- Use average loop run time last x loops to adjust sleep time accordingly as to meet goal sleep time
- Gmail or discord bot to check status when away
- Refactor all code to better adhere to best practices and style guides
- Refactor all JS scripts and HTML/CSS code.
- Log any change in sensor alias or position as to keep db working when moved
- Get live data order correct
- Add synthetic sensors like floor/roof delta
- Make data transfer tool to generate data for synthetic sensors with historical data
- Plot other significant data like stddev, stabilityscore, averages etc
- Sensor selector on mainpage

<h2>One day:</h2>

- Hourly average compared to normal average this time of night
- Separate main table into yearly main tables
- Weather forecast module
- External temp
- Log forecasted temp
- synthetic delta sensor for ext and forecasted temp
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
  - WiFi scanner and visualization tool

- Weather module
  - Predict/list rain/snow during the day

<h2>Completed items</h2>
- ~~Map interesting data regarding time/delta/other stuff since last peak or valley? See messenger dates jan 5th~~
- ~~Rate of change last x minutes~~
- ~~Degree hours in some way? (hours under x degrees within this period)~~
- ~~Stability score a la "1/stdavg"~~
- ~~Some kind of "temperature rise last hour for mainpage samt grader per min/time~~
- ~~Estimate energi in the system using volume of air~~
- ~~Calculate data regarding room energy and try to estimate heat input/output into the system~~
- ~~Deprecate storage_functions.py~~
- ~~Deprecate sensors.py~~
- ~~Refactor app.py~~
- ~~Merge old data to new DB data structure~~
- ~~Need new naming scheme for sensors datalogger.py~~
- ~~Refactor datalogger.py for it to easier adapt to different and new sensors~~
- ~~Make all historical data timescopes functional~~
- ~~Merge old data~~
- ~~data_logger.py status indicator~~
