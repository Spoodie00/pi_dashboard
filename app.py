import flask
import sensors
import storage_functions
from sensor_analytics import analytics
from sensor_controller import registry

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
def fetch_data():
     data = registry.get_all_sensor_data(pretty=True)
     return data

# TODO REMOVE AND REFACTOR WITH NEW DB STRUCTURE
@app.route("/api/stats/fetch_extremes", methods=["GET"])
def fetch_extremes():
     raw_dates = flask.request.args.get("todays_date")
     date_list = raw_dates.split(',') if raw_dates else []
     extremes_dict = storage_functions.get_extremes_data(["ds18b20_1", "sht33_1_humid", "sht33_1_temp"], date_list)
     return flask.jsonify(extremes_dict=extremes_dict)

@app.route("/api/get_graph_data", methods=["GET"])
def fetch_graph_data():
     start_date = flask.request.args.get("start_date")
     print(start_date)
     output = storage_functions.collect_all_data(start_date)
     return output

@app.route("/graph")
def grab_data_from_storage():
     return flask.render_template("graphing_page.html.j2")

@app.route("/todo")
def todopage():
     return flask.render_template("todo.html.j2")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)