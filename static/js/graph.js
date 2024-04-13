var eventSource = new EventSource('/data');

eventSource.onmessage = function(event) {
    var data = event.data.split(',');
    var x = data.slice(0, data.length / 2);
    var y = data.slice(data.length / 2);

    var ctx = document.getElementById('chartContainer').getContext('2d');

    if (!window.chart) {
        window.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: x,
                datasets: [{
                    label: 'Data',
                    data: y,
                    borderWidth: 1,
                    borderColor: 'red'
                }]
            },
            options: {
                responsive: false
            }
        });
    } else {
        window.chart.data.labels = x;
        window.chart.data.datasets[0].data = y;
        window.chart.update();
    }
};