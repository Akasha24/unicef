const DISTRICTS = [
  "beed",
  "Chhatrapati Sambhajinagar",
  "Dhule",
  "Jalgaon",
  "Jalna",
  "Wardha",
  "Yavatmal",
];

const DAYS_OF_WEEK = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

let temperatureChart = null;

function $(id) {
  return document.getElementById(id);
}

function today() {
  const d = new Date();
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function getTemperatureColor(temp) {
  if (temp >= 41) return "#db4437"; // Red (unsafe)
  if (temp >= 38) return "#f57c00"; // Orange (moderate)
  return "#2e7d32"; // Green (safe)
}

function getTemperatureTextColor(temp) {
  if (temp >= 41) return "#c5221f"; // Dark red
  if (temp >= 38) return "#e65100"; // Dark orange
  return "#1b5e20"; // Dark green
}

function getDayOfWeek(dateStr) {
  const date = new Date(dateStr + "T00:00:00");
  return DAYS_OF_WEEK[date.getUTCDay()];
}

function getUnsafeDaysCount(predictions) {
  return predictions.filter((p) => p.Predicted_Tmax >= 41).length;
}

function showAlert(message) {
  const alertBox = $("alertBox");
  const alertText = $("alertText");
  alertText.textContent = message;
  alertBox.classList.remove("hidden");
}

function hideAlert() {
  $("alertBox").classList.add("hidden");
}

function hideChart() {
  $("chartContainer").classList.add("hidden");
}

function showChart() {
  $("chartContainer").classList.remove("hidden");
}

function hideTable() {
  $("tableContainer").classList.add("hidden");
}

function showTable() {
  $("tableContainer").classList.remove("hidden");
}

function renderChart(predictions) {
  const labels = predictions.map((p) => {
    const dow = getDayOfWeek(p.Date);
    const day = new Date(p.Date + "T00:00:00").getUTCDate();
    return `${dow}\n${day}`;
  });

  const values = predictions.map((p) => p.Predicted_Tmax);
  const colors = values.map((v) => getTemperatureColor(v));
  const borderColors = colors.map((c) => c);

  const ctx = $("temperatureChart").getContext("2d");

  if (temperatureChart) {
    temperatureChart.destroy();
  }

  temperatureChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Predicted Tmax (°C)",
          data: values,
          backgroundColor: colors,
          borderColor: borderColors,
          borderWidth: 2,
          borderRadius: 12,
          borderSkipped: false,
          barThickness: "flex",
          barPercentage: 0.8,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              return `${context.parsed.y}°C`;
            },
          },
          backgroundColor: "rgba(0, 0, 0, 0.8)",
          padding: 8,
          titleFont: { size: 12, weight: "bold" },
          bodyFont: { size: 14, weight: "bold" },
        },
        datalabels: {
          anchor: "end",
          align: "top",
          font: {
            weight: "bold",
            size: 12,
          },
          color: (context) => getTemperatureTextColor(context.dataset.data[context.dataIndex]),
        },
      },
      scales: {
        y: {
          beginAtZero: false,
          min: 20,
          max: 50,
          ticks: {
            stepSize: 5,
            font: { size: 11 },
          },
          grid: {
            color: "rgba(0, 0, 0, 0.05)",
            drawBorder: false,
          },
        },
        x: {
          ticks: {
            font: { size: 11 },
          },
          grid: {
            display: false,
          },
        },
      },
    },
  });

  showChart();
}

function renderTable(predictions) {
  const tableBody = $("tableBody");
  tableBody.innerHTML = predictions
    .map((p, idx) => {
      const dow = getDayOfWeek(p.Date);
      const temp = p.Predicted_Tmax;
      let tempClass = "temp-low";
      if (temp >= 41) tempClass = "temp-high";
      else if (temp >= 38) tempClass = "temp-medium";

      const actualTmax = p.Actual_Tmax !== undefined ? p.Actual_Tmax : "N/A";
      const rmse = p.RMSE !== undefined ? p.RMSE : "N/A";

      return `
        <tr>
          <td>${p.Day}</td>
          <td>${p.Date}</td>
          <td>${dow}</td>
          <td><span class="temp-value ${tempClass}">${temp}°C</span></td>
          <td>${actualTmax === "N/A" ? "N/A" : actualTmax + "°C"}</td>
          <td>${rmse === "N/A" ? "N/A" : rmse}</td>
        </tr>
      `;
    })
    .join("");
  showTable();
}

function populateDistricts() {
  const select = $("district");
  DISTRICTS.forEach((district) => {
    const option = document.createElement("option");
    option.value = district;
    option.textContent = district;
    select.appendChild(option);
  });
}

async function doPredict() {
  const district = $("district").value.trim();
  const date = $("date").value.trim();

  if (!district) {
    showAlert("⚠ Please select a district");
    return;
  }

  if (!date) {
    showAlert("⚠ Please select a date");
    return;
  }

  hideAlert();
  hideChart();
  hideTable();

  const predictBtn = $("predictBtn");
  predictBtn.disabled = true;
  predictBtn.textContent = "Loading...";

  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        district: district,
        date: date,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      let errorMsg = errorData.error || `HTTP ${response.status}`;
      if (errorData.detail) {
        errorMsg += `: ${errorData.detail}`;
      }
      if (errorData.trace && errorData.trace.length > 0) {
        // Show simplified trace (last 500 chars)
        errorMsg += `\n\nTrace:\n${errorData.trace.slice(-500)}`;
      }
      throw new Error(errorMsg);
    }

    const data = await response.json();
    const predictions = data.predictions || [];
    const metrics = data.metrics || [];

    if (predictions.length === 0) {
      showAlert("No predictions returned");
      return;
    }

    // Check for unsafe days
    const unsafeDays = getUnsafeDaysCount(predictions);
    if (unsafeDays > 0) {
      showAlert(
        `⚠ Next ${unsafeDays} days unsafe for spraying (Tmax ≥ 41°C). Plan irrigation today.`
      );
    }

    renderChart(predictions);
    renderTable(metrics.length > 0 ? metrics : predictions);
  } catch (error) {
    showAlert(`Error: ${error.message}`);
  } finally {
    predictBtn.disabled = false;
    predictBtn.textContent = "Get Forecast";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  populateDistricts();
  $("date").value = today();

  $("predictBtn").addEventListener("click", doPredict);

  // Allow Enter key to submit
  $("date").addEventListener("keypress", (e) => {
    if (e.key === "Enter") doPredict();
  });

  $("district").addEventListener("keypress", (e) => {
    if (e.key === "Enter") doPredict();
  });
});
