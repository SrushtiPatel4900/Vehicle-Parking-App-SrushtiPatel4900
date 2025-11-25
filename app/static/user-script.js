document.addEventListener("DOMContentLoaded", async () => {
    try {
        const response = await fetch("/user/charts/data");
        const data = await response.json();

        const ctx = document.getElementById("historyChart").getContext("2d");

        new Chart(ctx, {
            type: "bar",
            data: {
                labels: ["Active Parkings", "Released Parkings"],
                datasets: [{
                    label: "Number of Cars",
                    data: [data.active, data.released],
                    backgroundColor: ["#36A2EB", "#4BC0C0"]
                },
                {
                    label: "Total Cost (Released)",
                    data: [0, data.total_cost],  // Show cost only in "Released"
                    backgroundColor: ["#ffffff00", "#FF6384"],
                    type: 'bar'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Your Parking Activity Overview'
                    }
                }
            }
        });

    } catch (err) {
        console.error("Failed to load chart data", err);
    }
});
