function refresh_text(id, data) {
  div = document.getElementById(id);
  div.textContent = `${data.reading.toFixed(2)} ${data.unit}`;
  div.classList.remove("animate_number_updated");
  void div.offsetWidth;
  div.classList.add("animate_number_updated");
}

function view_mode_basic() {
  room_energy_element = document.getElementById("room_energy_element");
  adv_sensor_data_elements = document.getElementsByClassName("adv_info_div");
  basic_view_button = document.getElementById(
    "adv_data_view_selector_button_basic",
  );
  adv_view_button = document.getElementById(
    "adv_data_view_selector_button_adv",
  );

  for (const element of adv_sensor_data_elements) {
    element.style.display = "none";
  }

  room_energy_element.style.visibility = "hidden";
  basic_view_button.style.fontWeight = "bold";
  basic_view_button.style.textDecoration = "underline";
  adv_view_button.style.fontWeight = "normal";
  adv_view_button.style.textDecoration = "none";

  adv_mode = false;
}

async function view_mode_adv() {
  room_energy_element = document.getElementById("room_energy_element");
  adv_sensor_data_elements = document.getElementsByClassName("adv_info_div");
  basic_view_button = document.getElementById(
    "adv_data_view_selector_button_basic",
  );
  adv_view_button = document.getElementById(
    "adv_data_view_selector_button_adv",
  );

  if (adv_mode === false && adv_data_fetched === false) {
    const url = `/api/fetch_adv_live_data`;
    const response = await fetch(url);
    const datapacket = await response.json();
    console.log(datapacket);
    const url2 = `/api/fetch_room_data`;
    const response2 = await fetch(url2);
    const datapacket2 = await response2.json();
    console.log(datapacket2);
    insert_advanced_data(datapacket, datapacket2);
    adv_data_fetched = true;
  }

  for (const element of adv_sensor_data_elements) {
    element.style.display = "block";
  }

  room_energy_element.style.visibility = "visible";
  basic_view_button.style.fontWeight = "normal";
  basic_view_button.style.textDecoration = "none";
  adv_view_button.style.fontWeight = "bold";
  adv_view_button.style.textDecoration = "underline";
  adv_mode = true;
}

function insert_advanced_data(datapacket, roomdata) {
  for (const [name, sensor_object] of Object.entries(datapacket)) {
    local_max_container = document.getElementById(`${name}_local_max`);
    local_max_ts_container = document.getElementById(`${name}_local_max_time`);
    if (sensor_object.recent_local_max === null) {
      local_max_container.innerHTML = "No local max so far today";
      local_max_ts_container.style.visibility = "hidden";
    } else {
      local_max_container.innerHTML = `${sensor_object.recent_local_max.val} ${sensor_object.unit}`;
      local_max_ts_container.innerHTML = `${sensor_object.recent_local_max.timedelta} (${sensor_object.recent_local_max.time})`;
    }

    local_min_container = document.getElementById(`${name}_local_min`);
    local_min_ts_container = document.getElementById(`${name}_local_min_time`);
    if (sensor_object.recent_local_min === null) {
      local_min_container.innerHTML = "No local max so far today";
      local_min_ts_container.style.visibility = "hidden";
    } else {
      local_min_container.innerHTML = `${sensor_object.recent_local_min.val} ${sensor_object.unit}`;
      local_min_ts_container.innerHTML = `${sensor_object.recent_local_min.timedelta} (${sensor_object.recent_local_min.time})`;
    }

    trend_container = document.getElementById(`${name}_trend`);
    trend_container.innerHTML = sensor_object.trend;

    rate_of_change_container = document.getElementById(
      `${name}_rate_of_change`,
    );
    rate_of_change_container.innerHTML = sensor_object.hourly_delta;

    stability_score_container = document.getElementById(
      `${name}_stability_score`,
    );
    stability_score_container.innerHTML = sensor_object.stability_score;

    hours_above_container = document.getElementById(`${name}_target_val`);
    hours_above_container.innerHTML = `${sensor_object.target_val} ${sensor_object.unit}`;

    hours_above_container = document.getElementById(`${name}_hours_above`);
    hours_above_container.innerHTML = sensor_object.time_above_target;
  }

  avg_room_temp_container = document.getElementById("avg_room_temp");
  avg_room_temp_container.innerHTML = roomdata.avg_room_temp;

  room_energy_container = document.getElementById("spec_room_energy");
  room_energy_container.innerHTML = roomdata.room_spec_heat;

  room_heat_input = document.getElementById("room_energy_input");
  room_heat_input.innerHTML = roomdata.room_energy_delta;
}

async function gather_temp_data() {
  const url = `/api/fetch_sensor_data`;
  const response = await fetch(url);
  const datapacket = await response.json();
  console.log(datapacket);
  return datapacket;
}

function makeDivs(response_object) {
  const container = document.getElementById("sensor_container");
  container.classList.remove("animate_number_updated");
  Object.entries(response_object).forEach(([id, data]) => {
    const wrapper = document.createElement("div");

    val = data.reading.toFixed(2);

    wrapper.innerHTML = `
      <div class="sensor_name_div">${data.display_name}</div>
      <div class="sensor_data_div" id="${id}">${val} ${data.unit}</div>
      <div class="adv_info_div" id="adv_sensor_data_element">
        <div class="adv_info_horizontal_divider"></div>
        <div class="adv_info_line">
          <span>Stability score today:</span>
          <span class="adv_info_line_var" id="${id}_stability_score"></span>
        </div>
        <div class="adv_info_line">
          <span>Last local max:</span>
          <span class="adv_info_line_var" id="${id}_local_max"></span>
        </div>
        <div class="adv_info_line">
          <span>ΔT since last local max:</span>
          <span class="adv_info_line_var" id="${id}_local_max_time"></span>
        </div>
        <div class="adv_info_line">
          <span>Last local min:</span>
          <span class="adv_info_line_var" id="${id}_local_min"></span>
        </div>
        <div class="adv_info_line">
          <span>ΔT since last local min:</span>
          <span class="adv_info_line_var" id="${id}_local_min_time"></span>
        </div>
        <div class="adv_info_line">
          <span>Current trend:</span>
          <span class="adv_info_line_var" id="${id}_trend"></span>
        </div>
        <div class="adv_info_line">
          <span>Current rate of change:</span>
          <span class="adv_info_line_var" id="${id}_rate_of_change"></span>
          <span class="adv_info_line_var" id="${id}_rate_of_change_unit">${data.unit} per hour</span>
        </div>
        <div class="adv_info_line">
          <span>Target value:</span>
          <span class="adv_info_line_var" id="${id}_target_val"></span>
        </div>
        <div class="adv_info_line">
          <span>Time above target value today:</span>
          <span class="adv_info_line_var" id="${id}_hours_above"></span>
        </div>
      </div>
    `;
    container.appendChild(wrapper);
  });
  container.classList.add("animate_number_updated");
}

async function handleData() {
  sensor_data = await gather_temp_data();
  if (divs_made == false) {
    makeDivs(sensor_data);
    divs_made = true;
  } else {
    Object.entries(sensor_data).forEach(([id, data]) => {
      refresh_text(id, data);
    });
  }

  setTimeout(handleData, 60000);
}

divs_made = false;
adv_mode = false;
adv_data_fetched = false;

handleData();
