async function gather_temp_data(date, sensors, sample) {
  var json_list = JSON.stringify(sensors);
  const url = `/api/graph_data?day_delta=${date}&sensors=${json_list}&sampling=${sample}`;
  const response = await fetch(url);
  const datapacket = await response.json();
  console.log(datapacket);
  return datapacket;
}

function getRandomColor() {
  var letters = "0123456789ABCDEF";
  var color = "#";
  for (var i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)];
  }
  return color;
}

async function get_avaliable_sensors() {
  const url = `/api/avaliable_sensors`;
  const response = await fetch(url);
  const sensor_dict = await response.json();
  return sensor_dict;
}

function set_avaliable_sensors_in_selector(sens_dict) {
  selector_box = document.getElementById("sensor_selector");
  for (const [key, value] of Object.entries(sens_dict)) {
    selector_box.options[selector_box.options.length] = new Option(
      value.display_name
    );
  }
}

async function fetch_new_chart_data() {
  sensor_array = [];
  tempChart.data.datasets = [];

  var sensor_selector = document.getElementById("sensor_selector");
  var selected_sensors = sensor_selector.selectedOptions;
  for (let i = 0; i < selected_sensors.length; i++) {
    sensor_name = selected_sensors[i].label;
    sensor_array.push(avaliable_sensors[sensor_name]);
  }

  var raw_time_scope = document.getElementById("time_selector").value;
  var timescope = timescope_to_delta[raw_time_scope];
  var sampling = document.getElementById("sampling_selector").value;

  const datapacket = await gather_temp_data(timescope, sensor_array, sampling);

  tempChart.data.labels = Object.values(datapacket)[0]["ts"];

  for (const [key, value] of Object.entries(datapacket)) {
    label_string = key.replace(/_/g, " ");
    color = getRandomColor();
    if (Object.keys(value.colors).length !== 0) {
      for (const [param, color_id] of Object.entries(value.colors)) {
        if (label_string.includes(param)) {
          color = color_id;
        }
      }
    } else {
      color = getRandomColor();
    }
    tempChart.data.datasets.push({
      label: label_string,
      data: value.values,
      fill: false,
      borderColor: color,
      backgroundColor: color,
      lineTension: 0.1,
      pointStyle: "circle",
    });
  }
  tempChart.update();
}

function alter_selector_p() {
  const sensor_selector = document.getElementById("sensor_selector");
  const selected_sensors = sensor_selector.selectedOptions;
  const num_selected_sensors = selected_sensors.length;
  if (num_selected_sensors == 1) {
    document.getElementById("select_text").innerHTML = "for the last";
  } else {
    document.getElementById("select_text").innerHTML = "sensors for the last";
  }
}

function set_sample_options() {
  const time_scope = document.getElementById("time_selector");
  const selected_time_scope = time_scope.options[time_scope.selectedIndex].text;
  const selector_box = document.getElementById("sampling_selector");
  selector_box.options.length = 0;
  array = sample_rates[selected_time_scope];
  array.forEach((element) => {
    selector_box.options[selector_box.options.length] = new Option(element);
  });
}

function change_y_axis_start() {
  const yScale = tempChart.options.scales.y;
  if (yScale.min === 0) {
    yScale.min = undefined;
  } else {
    yScale.min = 0;
  }
  tempChart.update();
  axis_button = document.getElementById("axis_button");
  if (axis_button.innerHTML === "Begin Y-axis at 0: false") {
    axis_button.innerHTML = "Begin Y-axis at 0: true";
  } else {
    axis_button.innerHTML = "Begin Y-axis at 0: false";
  }
}

async function init_chart() {
  avaliable_sensors = await get_avaliable_sensors();
  sensor_selector = document.getElementById("sensor_selector");
  set_sample_options();
  const pre_selected_options = ["Floor temperature", "Head height temperature"];

  for (const [key, value] of Object.entries(avaliable_sensors)) {
    const shouldBeSelected = pre_selected_options.includes(key);
    sensor_selector.options[sensor_selector.options.length] = new Option(
      key,
      key,
      shouldBeSelected,
      shouldBeSelected
    );
  }

  var ctx = document.getElementById("tempChart").getContext("2d");
  tempChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: null,
      datasets: [],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          labels: {
            usePointStyle: true,
          },
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              let value = Number(context.raw);
              return `Value: ${value.toFixed(2)}`;
            },
          },
        },
      },
    },
  });
  fetch_new_chart_data();
}

var avaliable_sensors = {};
var timescope_to_delta = { day: 1, week: 7, month: 30, year: 365 };
var sample_rates = {
  day: [3, 10],
  week: [1, 3, 5, 10],
  month: [1],
  year: [1, 3, 5, 10],
};
var tempChart = null;

window.addEventListener("DOMContentLoaded", init_chart);
