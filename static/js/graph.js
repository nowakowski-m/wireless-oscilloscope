var eventSource = new EventSource('/data');
var graph_voltage_range = 5; //has to be set to default voltage scale input value
var graph_dc_offset = 0; //has to be set to default dc offset input value

function updateButtonText(flag) {
    var button = document.getElementById("toggleButton");
    button.textContent = flag ? "Stop" : "Start";
}

function toggleFlag() {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/toggle_flag", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    // xhr.onload = function () {
    //     if (xhr.status === 200) {
    //         var flag = JSON.parse(xhr.responseText).flag;
    //         updateButtonText(flag);
    //     }
    // };
    
    xhr.send();
}

eventSource.onmessage = function(event) {
    var data = event.data.split(',');
    var x = data.slice(0, data.length / 2);
    var y = data.slice(data.length / 2);

    var ctx = document.getElementById('chartContainer').getContext('2d');
    
    document.getElementById('voltageRange').addEventListener('input', function() { graph_voltage_range = parseFloat(this.value);});
    document.getElementById('dcOffset').addEventListener('input', function() { graph_dc_offset = parseFloat(this.value);});

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
                        min: ((graph_voltage_range * (-1)) + graph_dc_offset),
                        max: (graph_voltage_range + graph_dc_offset)
                    }
                }
            }
        });
    } else {
        window.chart.data.labels = x;
        window.chart.data.datasets[0].data = y;
        window.chart.options.scales.y.min = ((graph_voltage_range * (-1)) + graph_dc_offset);
        window.chart.options.scales.y.max = (graph_voltage_range + graph_dc_offset);
        window.chart.update();
    }
};