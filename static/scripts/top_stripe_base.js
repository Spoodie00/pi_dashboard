function get_iso_ts(daysAgo) {
  const d = new Date();
  d.setDate(d.getDate() - daysAgo);
  const hour_diff = Math.abs(d.getTimezoneOffset()) / 60;
  d.setHours(d.getHours() + 1);

  let iso_d = d.toISOString();
  iso_d = iso_d.slice(0, -8);
  return iso_d;
}

document.getElementById("live_view").onclick = function () {
  location.href = `/live`;
};

document.getElementById("historical_data").onclick = function () {
  location.href = `/graph`;
};

document.getElementById("stats").onclick = function () {
  location.href = `/stats`;
};
