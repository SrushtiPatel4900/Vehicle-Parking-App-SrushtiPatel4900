document.addEventListener('DOMContentLoaded', function () {
    fetch('/admin/charts/data')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('bookingChart').getContext('2d');

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.lot_names,
                    datasets: [
                        {
                            label: 'Booked Spots',
                            data: data.booked_counts,
                            backgroundColor: 'rgba(255, 99, 132, 0.7)',
                            stack: 'Stack 0'
                        },
                        {
                            label: 'Available Spots',
                            data: data.available_counts,
                            backgroundColor: 'rgba(75, 192, 192, 0.7)',
                            stack: 'Stack 0'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Parking Spot Status by Lot'
                        }
                    },
                    scales: {
                        x: {
                            stacked: true
                        },
                        y: {
                            stacked: true,
                            beginAtZero: true,
                            precision: 0
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error loading chart data:', error);
        });
});
