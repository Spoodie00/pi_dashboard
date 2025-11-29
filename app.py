import flask
import sensors
import storage_functions

print("Running app.py")
app = flask.Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching for static files

@app.route("/")
def default_site():
     return flask.render_template("default.html.j2")

@app.route("/live")
def hello_world():
     return flask.render_template("mainpage.html.j2")

@app.route("/api/fetch_sensor_data", methods=["GET"])
def fetch_sht33_data():
     probeid = flask.request.args.get("probeid")     
     ds18b20_temp = sensors.get_ds18b20_temp(probeid)
     sht33_data = sensors.sht33_reading()
     sht33_temp = sht33_data[0]
     sht33_humid = sht33_data[1]
     return flask.jsonify(ds18b20=ds18b20_temp, sht33_temp=sht33_temp, sht33_humid=sht33_humid)

@app.route("/api/stats/fetch_extremes", methods=["GET"])
def fetch_extremes():
     raw_dates = flask.request.args.get("todays_date")
     date_list = raw_dates.split(',') if raw_dates else []
     extremes_dict = storage_functions.get_extremes_data(["ds18b20_1", "sht33_1_humid", "sht33_1_temp"], date_list)
     return flask.jsonify(extremes_dict=extremes_dict)

@app.route("/graph")
def grab_data_from_storage():
     start_date = flask.request.args.get("start_date")
     datapoints = storage_functions.collect_data(start_date)

     return flask.render_template("graphing_page.html.j2", labels=datapoints[0], temp_ds18b20=datapoints[1], temp_sht33=datapoints[2], humid_sht33=datapoints[3])

@app.route("/stats")
def statspage():  
     return flask.render_template("stats.html.j2")

@app.route("/todo")
def todopage():
     return flask.render_template("todo.html.j2")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)