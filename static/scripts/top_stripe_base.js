function get_iso_ts(daysAgo) {
  const d = new Date();
  d.setDate(d.getDate() - daysAgo);
  const hour_diff = Math.abs(d.getTimezoneOffset()) / 60;
  d.setHours(d.getHours() + 1);

  let iso_d = d.toISOString();
  iso_d = iso_d.slice(0, -8);
  return iso_d;
}

document.getElementById("day_avg").onclick = function () {
  dateString = get_iso_ts(1);
  location.href = `/graph?start_date=${dateString}`;
};

document.getElementById("week_avg").onclick = function () {
  dateString = get_iso_ts(7);
  location.href = `/graph?start_date=${dateString}`;
};

document.getElementById("live_view").onclick = function () {
  location.href = `/live`;
};

document.getElementById("stats").onclick = function () {
  location.href = `/stats`;
};
