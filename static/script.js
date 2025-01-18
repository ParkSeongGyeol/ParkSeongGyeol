document.getElementById("fetch-data").addEventListener("click", () => {
    fetch("/api/data")
        .then(response => response.json())
        .then(data => {
            updateTable(data);
            updateCharts(data);
        });
});

function updateTable(data) {
    const tableBody = document.querySelector("#data-table tbody");
    tableBody.innerHTML = ""; // Clear table rows

    data.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${row.timestamp}</td>
            <td>${row.temperature}°C</td>
            <td>${row.humidity}%</td>
            <td>${row.co2}</td>
            <td>${row.density}</td>
            <td>${row.alcohol}</td>
            <td>${row.sugar}</td>
        `;
        tableBody.appendChild(tr);
    });
}

function updateCharts(data) {
    const labels = data.map(d => d.timestamp);
    const temperature = data.map(d => d.temperature);
    const humidity = data.map(d => d.humidity);

    if (window.envChart) window.envChart.destroy();
    if (window.progressChart) window.progressChart.destroy();

    const ctx1 = document.getElementById("envChart").getContext("2d");
    window.envChart = new Chart(ctx1, {
        type: "line",
        data: {
            labels,
            datasets: [
                {
                    label: "Temperature",
                    data: temperature,
                    borderColor: "red",
                    fill: false
                },
                {
                    label: "Humidity",
                    data: humidity,
                    borderColor: "blue",
                    fill: false
                }
            ]
        }
    });
}