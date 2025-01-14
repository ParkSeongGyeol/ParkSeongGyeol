document.getElementById("fetch-data").addEventListener("click", () => {
    fetch("/api/data")
        .then(response => response.json())
        .then(data => {
            updateTable(data);
            updateChart(data);
        });
});

function updateTable(data) {
    const tableBody = document.querySelector("#data-table tbody");
    tableBody.innerHTML = ""; // Clear existing rows

    data.forEach(item => {
        const row = document.createElement("tr");
        const airQualityColor = getAirQualityColor(item.air_quality);

        row.innerHTML = `
            <td>${item.timestamp}</td>
            <td>${item.temperature}</td>
            <td>${item.humidity}</td>
            <td style="color: ${airQualityColor}; font-weight: bold;">${item.air_quality}</td>
        `;
        tableBody.appendChild(row);
    });
}

function updateChart(data) {
    const labels = data.map(item => item.timestamp);
    const temperatures = data.map(item => item.temperature);
    const humidities = data.map(item => item.humidity);

    if (window.chart) {
        window.chart.destroy(); // Clear the previous chart
    }

    const ctx = document.getElementById("dataChart").getContext("2d");
    window.chart = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Temperature (°C)",
                    data: temperatures,
                    borderColor: "red",
                    backgroundColor: "rgba(255, 99, 132, 0.2)",
                    fill: true
                },
                {
                    label: "Humidity (%)",
                    data: humidities,
                    borderColor: "blue",
                    backgroundColor: "rgba(54, 162, 235, 0.2)",
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

function getAirQualityColor(quality) {
    if (quality === "Good") return "green";
    if (quality === "Average") return "orange";
    if (quality === "Poor") return "red";
    return "black";
}