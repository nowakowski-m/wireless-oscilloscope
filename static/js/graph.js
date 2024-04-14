var eventSource = new EventSource('/data');
var graph_voltage_range = 0;
var graph_dc_offset = 0;

eventSource.onmessage = function(event) {
    var data = event.data.split(',');
    var x = data.slice(0, data.length / 2);
    var y = data.slice(data.length / 2);

    var ctx = document.getElementById('chartContainer').getContext('2d');
    
    document.getElementById('voltageRange').addEventListener('input', function() { graph_voltage_range = this.value;});
    document.getElementById('dcOffset').addEventListener('input', function() { graph_dc_offset = this.value;});

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
                responsive: false,
                scales: {
                    y: {
                        suggestedMin: -(graph_voltage_range) + graph_dc_offset,
                        suggestedMax: graph_voltage_range + graph_dc_offset
                    }
                }
            }
        });
    } else {
        window.chart.data.labels = x;
        window.chart.data.datasets[0].data = y;
        window.chart.options.scales.y.suggestedMin = -(graph_voltage_range) + graph_dc_offset;
        window.chart.options.scales.y.suggestedMax = graph_voltage_range + graph_dc_offset;
        window.chart.update();
    }
};