function refresh_text(text, data, suffix) {
  div = document.getElementById(text);
  div.textContent = data.toFixed(2) + suffix;
  div.classList.remove("animate_number_updated");
  void div.offsetWidth;
  div.classList.add("animate_number_updated");
}

async function gather_temp_data(probeid) {
  const url = `/api/fetch_sensor_data?probeid=${probeid}`;
  const response = await fetch(url);
  const data = await response.json();
  refresh_text("ds18b20_display", data.ds18b20, " Celsius");
  refresh_text(`sht33_temp`, data.sht33_temp, " Celsius");
  refresh_text(`sht33_humid`, data.sht33_humid, "% humidity");
  console.log(data)
}

gather_temp_data("28-3cb7e3819e17");

setInterval(function () {
  gather_temp_data("28-3cb7e3819e17");
}, 60000);
