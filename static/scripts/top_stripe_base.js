function get_timestamp_old(daysAgo) {
  const pad = (num) => num.toString().padStart(2, "0");

  const date = new Date();

  date.setDate(date.getDate() - daysAgo);

  var hours = pad(date.getHours());
  const minutes = pad(date.getMinutes());
  const day = pad(date.getDate());
  const month = pad(date.getMonth() + 1);
  const year = pad(date.getFullYear());

  if (hours < 1) {
    hours = 99;
  }

  return `${hours}${minutes}${day}${month}${year}`;
}

document.getElementById("day_avg").onclick = function () {
  dateString = get_timestamp_old(1);
  location.href = `/graph?start_date=${dateString}`;
};

document.getElementById("week_avg").onclick = function () {
  dateString = get_timestamp_old(7);
  location.href = `/graph?start_date=${dateString}`;
};

document.getElementById("live_view").onclick = function () {
  location.href = `/live`;
};

document.getElementById("stats").onclick = function () {
  location.href = `/stats`;
};
