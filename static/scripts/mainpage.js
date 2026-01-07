function refresh_text(id, data) {
  div = document.getElementById(id);
  div.textContent = data.toFixed(2);
  div.classList.remove("animate_number_updated");
  void div.offsetWidth;
  div.classList.add("animate_number_updated");
}

async function gather_temp_data() {
  const url = `/api/fetch_sensor_data`;
  const response = await fetch(url);
  const datapacket = await response.json();
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
      <div id="${id}" class="sensor_data_div">${val} ${data.unit}</div>
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

handleData();
