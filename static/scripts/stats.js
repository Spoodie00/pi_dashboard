const tabs = document.querySelectorAll("[data-tab-target]");
const tab_container = document.querySelectorAll(".data_container");
const buttons = document.querySelectorAll(".date_selector_button");

function get_timestamp(daysAgo) {
  const pad = (num) => num.toString().padStart(2, "0");

  const date = new Date();

  date.setDate(date.getDate() - daysAgo);

  const day = pad(date.getDate());
  const month = pad(date.getMonth() + 1);
  const year = pad(date.getFullYear());

  return `${year}-${month}-${day}`;
}

tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    tab_container.forEach((content) => {
      content.classList.remove("active");
    });

    const target = document.querySelector(tab.dataset.tabTarget);
    target.classList.add("active");
  });
});

buttons.forEach((button) => {
  button.addEventListener("click", () => {
    buttons.forEach((btn) => btn.classList.remove("active"));
    button.classList.add("active");
  });
});

const timestamps = [
  get_timestamp(1),
  get_timestamp(7),
  get_timestamp(30),
  get_timestamp(365),
  "1970-03-01",
];
let extremes_dict = null;

async function collect_extremes() {
  if (extremes_dict == null) {
    const url = `/api/stats/fetch_extremes?todays_date=${timestamps}`;
    const response = await fetch(url);
    const data = await response.json();
    extremes_dict = data.extremes_dict;
    console.log(extremes_dict);
  }
  return extremes_dict;
}

const box_ids = ["ds18b20_1", "sht33_1_temp", "sht33_1_humid"];
const suffixes = ["_max", "_max_ts", "_min", "_min_ts"];

async function handle_backend_response(date) {
  const extremes_dict = await collect_extremes();

  box_ids.forEach((box_id) => {
    suffixes.forEach((suffix) => {
      id_string = box_id.concat(suffix);
      text_box = document.getElementById(id_string);
      text_box.textContent = extremes_dict[box_id.concat(suffix, "_", date)];
    });
  });
}

handle_backend_response(get_timestamp(1));
