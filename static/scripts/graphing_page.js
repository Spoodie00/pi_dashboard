window.addEventListener("DOMContentLoaded", function () {
  var ctx = document.getElementById("tempChart").getContext("2d");
  var tempChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: window.graphData.labels,
      datasets: [
        {
          label: "Floor temperature",
          data: window.graphData.temp_ds18b20,
          fill: false,
          borderColor: "rgb(75, 75, 75)",
          lineTension: 0.1,
        },
        {
          label: "Wall temperature",
          data: window.graphData.temp_sht33,
          fill: false,
          borderColor: "rgb(50, 10, 200)",
          lineTension: 0.1,
        },
        {
          label: "Humidity",
          data: window.graphData.humid_sht33,
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
});
