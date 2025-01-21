document.getElementById("fetch-data").addEventListener("click", () => {
    fetch("/api/data")
        .then(response => response.json())
        .then(data => {
            updateTable(data);
            updateCharts(data);
        })
        .catch(error => console.error("Error fetching data:", error));
});

// 테이블 업데이트
function updateTable(data) {
    const tableBody = document.querySelector("#data-table");
    tableBody.innerHTML = ""; // 기존 데이터 초기화

    data.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${row.timestamp}</td>
            <td>${row.temperature.toFixed(2)} °C</td>
            <td>${row.humidity.toFixed(2)} %</td>
            <td>${row.co2.toFixed(2)} ppm</td>
            <td>${row.density}</td>
            <td>${row.alcohol}</td>
            <td>${row.sugar}</td>
        `;
        tableBody.appendChild(tr);
    });
}

// 차트 업데이트
function updateCharts(data) {
    const labels = data.map(d => d.timestamp);
    const temperatures = data.map(d => d.temperature);
    const humidities = data.map(d => d.humidity);

    const ctx1 = document.getElementById("lineChart").getContext("2d");
    if (window.lineChart) {
        window.lineChart.destroy();
    }
    window.lineChart = new Chart(ctx1, {
        type: "line",
        data: {
            labels,
            datasets: [{
                label: "Temperature (°C)",
                data: temperatures,
                borderColor: "rgba(255, 99, 132, 1)",
                backgroundColor: "rgba(255, 99, 132, 0.2)",
                tension: 0.3,
            }]
        }
    });

    const ctx2 = document.getElementById("barChart").getContext("2d");
    if (window.barChart) {
        window.barChart.destroy();
    }
    window.barChart = new Chart(ctx2, {
        type: "bar",
        data: {
            labels,
            datasets: [{
                label: "Humidity (%)",
                data: humidities,
                backgroundColor: "rgba(54, 162, 235, 0.6)",
            }]
        }
    });
}
