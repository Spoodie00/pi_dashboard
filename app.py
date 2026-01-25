import flask
import json
import subprocess
import config
from sensor_analytics import analytics
from sensor_controller import registry
from database_analytics import fetch_from_db
from livereload import Server
from datetime import datetime

app = flask.Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching for static files
live_data = {"data": None, "ts": 0}
adv_live_data = None

@app.route("/")
def default_site():
     return flask.render_template("default.html.j2")

@app.route("/live")
def hello_world():
     return flask.render_template("mainpage.html.j2")

@app.route("/api/fetch_adv_live_data")
def fetch_adv_live_data():
     global adv_live_data
     adv_live_data = fetch_from_db.adv_live_data()
     return adv_live_data

@app.route("/api/fetch_sensor_data", methods=["GET"])
def fetch_data():
     global live_data
     global adv_live_data
     ts = datetime.now().timestamp()
     if ts > (live_data["ts"] + 60):
          live_data = {"data": registry.get_all_sensor_data(pretty=True), "ts": ts}
     return live_data["data"]

@app.route("/api/fetch_room_data")
def fetch_room_data():
     global live_data
     global adv_live_data
     return analytics.compute_room_stats(live_data["data"], adv_live_data)

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

@app.route("/api/logger_status")
def get_logger_status():
     filename = config.datalogger_filename
     pytonProcess = subprocess.check_output(f"ps -ef | grep {filename}",shell=True).decode()
     pytonProcess = pytonProcess.split('\n')

     for process in pytonProcess:
          if filename and "python" in process:
               return json.dumps(True)
     
     return json.dumps(False)

@app.route("/api/test")
def test_endpoint():
     print(flask.request.args)
     return {}

if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=5000, debug=True)
     server = Server(app.wsgi_app)
     server.watch("templates/*.html.j2")
     server.serve(host='0.0.0.0', port=5000, debug=True)