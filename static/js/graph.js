var eventSource = new EventSource('/data');
        eventSource.onmessage = function(event) {
            // Parsing data from CSV.
            var data = event.data.split(',');
            var x = data.slice(0, data.length / 2);
            var y = data.slice(data.length / 2);

            // Checking if Chart already exists.
            if (window.chart instanceof Chart) {
                window.chart.destroy(); // If yes, we need to remove existing one.
            }

            // Creating new graph.
            var ctx = document.getElementById('chart').getContext('2d');
            window.chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: x,
                    datasets: [{
                        label: 'Data',
                        data: y,
                        backgroundColor: 'rgba(0, 119, 204, 0.3)',
                        borderColor: 'rgba(0, 119, 204, 0.8)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        };