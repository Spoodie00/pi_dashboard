async function gather_temp_data() {
  const url = `/api/get_graph_data?start_date=2025-12-13T12:00`;
  const response = await fetch(url);
  const datapacket = await response.json();
  return datapacket;
}

async function init_chart() {
  const datapacket = await gather_temp_data();
  var ctx = document.getElementById("tempChart").getContext("2d");
  var tempChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: datapacket["labels"],
      datasets: [
        {
          label: "Floor temperature",
          data: datapacket["ds18b20"],
          fill: false,
          borderColor: "rgb(75, 75, 75)",
          lineTension: 0.1,
        },
        {
          label: "Wall temperature",
          data: datapacket["sht33t"],
          fill: false,
          borderColor: "rgb(50, 10, 200)",
          lineTension: 0.1,
        },
        {
          label: "Humidity",
          data: datapacket["sht33h"],
          fill: false,
          borderColor: "rgb(150, 30, 30)",
          lineTension: 0.1,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
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
}

window.addEventListener("DOMContentLoaded", init_chart);
