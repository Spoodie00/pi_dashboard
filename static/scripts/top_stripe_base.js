document.getElementById("live_view").onclick = function () {
  location.href = `/live`;
};

document.getElementById("historical_data").onclick = function () {
  location.href = `/graph`;
};

document.getElementById("stats").onclick = function () {
  location.href = `/stats`;
};

window.addEventListener("DOMContentLoaded", async function () {
  const url = `/api/logger_status`;
  const response = await fetch(url);
  const datapacket = await response.json();
  indicator = this.document.getElementById("status_indicator");
  if (datapacket) {
    indicator.style.color = "#00be29";
    indicator.style.textShadow = "0px 0px 8px #00be29";
  } else {
    indicator.style.color = "#a10000";
    indicator.style.textShadow = "0px 0px 8px #a10000";
  }
});
