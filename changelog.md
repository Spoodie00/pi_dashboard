<h2></h2>

- Added an advanced view on the live page with a bunch of interesting datapoints both per sensor and for the system as a whole
- Datalogger status indicator
- Added configurable units and hardware name config on a per sensor basis
- Adjusted the graph display labels to use the sensor display name
- Optimized live data sensor reading
- Bunch of small bug fixes
- fixed a typo in the html-title tag

<h2>13.01.2026</h2>

- Reworked and improved graphing page
- Adjusted layout of menu bar to better reflect the tab contents
- Added database_fetcher.py for all the database needs of the graph page
- Deprecated sensors.py and storage_functions.py
- Updated app.py
- Renamed logging_data.db to sensor_database.db to better reflect its purpose
- Adjusted columns and names of db tables to better relfect their purpose
- Made datalogger pull stddev data from db (forgot to run function)
- Validated that the datalogger in-fact does pull from the DB
- Updated live page so it pulls avaliable sensors and relevant data from the config instead of being hardcoded
- Removed the reference to main.html which produced an insignificant 404 error
- Fixed bugs and did a ton of minor tweaks

<h2>08.01.2026</h2>

- Refactored/altered some html/css/js
- finished new db structure
- merged old data to new db structure
- bunch of small bugfixes
- refactored mainpage so it uses new db structure

<h2>01.01.2026</h2>

- Rewrote and simplified datalogger significantly (for the last time) for OOP
- Added drivers.py, sensor_analytics.py, sensor_controller.py and config.py to do the actual OOP in datalogger
- Added way more stuff in the todo section of readme.md
- Next up: write other files to make use of the new data structure

<h2>26.12.2025</h2>

- Finished inital version of datalogger.py barring ineviatble bugfixes, refactoring and optimization
- Updates readme.md with even more ideas and todo-points

<h2>23.12.2025</h2>

- "logging_of_temp.py" renamed to "datalogger.py" and rewritten from scratch (WIP, use logging_of_temp.py for now)
- Changed schema of logging_data.db and made copy to test datalogger.py before it goes live
- generated test data for datalogger.py
- updated readme.md with new ideas

<h2>07.12.2025</h2>

- Added new tables to db in preparation of new structure and refactoring
- minor changes to storage_functions

<h2>30.11.2025</h2>

- Migrated old (november 24 - may 25) data to main db
