import flask
import storage_functions
import json
from sensor_analytics import analytics
from sensor_controller import registry
from database_fetcher import fetch_from_db
from livereload import Server

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

@app.route("/api/graph_data", methods=["GET"])
def fetch_graph_data():
     day_delta = flask.request.args.get("day_delta")
     sensors = flask.request.args.get("sensors")
     sampling = flask.request.args.get("sampling")
     sensor_list = json.loads(sensors)
     formatted_dict = fetch_from_db.graph_data(day_delta, sampling, sensor_list)
     return formatted_dict

@app.route("/graph")
def grab_data_from_storage():
     return flask.render_template("graphing_page.html.j2")

@app.route("/api/avaliable_sensors")
def get_avaliable_sensors():
     return registry.get_avaliable_sensors()

@app.route("/api/test")
def test_endpoint():
     print(flask.request.args)
     return {}

if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=5000, debug=True)
     server = Server(app.wsgi_app)
     server.watch("templates/*.html.j2")
     server.serve(host='0.0.0.0', port=5000, debug=True)