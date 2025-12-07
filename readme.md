<h1>TODO:</h1>

<h2>Live data:</h2>

- Some kind of "temperature rise last hour for mainpage samt grader per min/time
- Estimer energien i rommet ut i fra volum luft, trykk etc, logg gjerne dette senere
- Masse data rundt romenergi, prøv å beregne snitteffekt for radiator

<h2>Historical data:</h2>

- Heatmap last 30 days to visualize average temps for the period
- Column plot to visualize distro of avg temps during last 30 days

<h2>Misc:</h2>

- Utvid stats siden med mer lignende info
- Grad-timer hadde vært kult "timer under x grader denne perioden" (hvordan gjøre dette i praksis?)
- Stability score a la "1/stdavg"
- Snittdata rundt våken og sove-tider
- Hva kan en gjøre mtp å estimere når jeg er hjemme/våken/varmer?
- Correlation matrix

<h2>En vakker dag</h2>

- Snittemp nå iforhold til vanlig temp denne tiden på døgnet, timesbasert
- separate main table into yearly main tables

<h2>Table plan:</h2>

- Main_storage (keeps every 15 min aggregate forever)

  - readings
  - ts

- live_stats (tracked every minute but pushed to db every 15, purged if older than 24 hours)

  - readings
  - ts

- quarterly-aggregate (15 min of data aggregated for each row, purged after a week, serves to offload main table)
  - readings
  - ts
  - one row per sensor per 15 min
- history (aggregate a day of data per line (pushed every 15 mins))
  - date
  - num_readings
  - aggregate
  - max_delta
  - min_delta
  - one line per sensor per day
- stats_table (cache of every key statistic requested by user, refreshed every 15 or 60 min, relieves stress on large tables)
