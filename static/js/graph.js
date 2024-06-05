var eventSource = new EventSource('/data');
var graph_voltage_range = 5; // has to be set to default voltage scale input value
var graph_dc_offset = 0; // has to be set to default dc offset input value

var isGenerating = true;

function updateButtonText() {
    var button = document.getElementById("toggleButton");
    button.textContent = isGenerating ? "Stop" : "Start";
}

function toggleFlag() {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/toggle_flag", true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.onload = function() {
        if (xhr.status === 200) {
            isGenerating = !isGenerating;
            updateButtonText();
        }
    };
    xhr.send(JSON.stringify({ toggle: true }));
}

document.addEventListener("DOMContentLoaded", function() {
    fetch("/get_flag_status")
        .then(response => response.json())
        .then(data => {
            isGenerating = data.isGenerating;
            updateButtonText();
        })
        .catch(error => console.error("Error fetching flag status:", error));
});

function setSamplingFreq(value) {
    document.getElementById('samplingFreqValue').innerText = value;
        fetch('/set_frequency', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ frequency: value })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        initializeChart();
    })
    .catch((error) => console.error('Error:', error));
}

function getTimeLabel(callback) {
    fetch('/sampling-period')
    .then(response => response.json())
    .then(data => {
        const samplingPeriod = data.sampling_period;
        const totalPoints = data.points_amount;

        const labels = [];
        const timeStep = 1 / (samplingPeriod / 2);

        for (let i = 0; i < totalPoints; i++) {
            const time = i / timeStep;
            labels.push(time.toFixed(3));
        }
        callback(labels);
    })
    .catch(error => {
        console.error('Error:', error);
        callback([]);
    });
}

function initializeChart() {
    getTimeLabel(function(label) {
        eventSource.onmessage = function(event) {
            var data = event.data.split(',');
            var x = label;
            var y = data;

            var ctx = document.getElementById('chartContainer').getContext('2d');
            
            document.getElementById('voltageRange').addEventListener('input', function() { graph_voltage_range = parseFloat(this.value); });
            document.getElementById('dcOffset').addEventListener('input', function() { graph_dc_offset = parseFloat(this.value); });

            if (!window.chart) {
                window.chart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: x,
                        datasets: [{
                            label: 'Voltage [V]',
                            data: y,
                            borderWidth: 1,
                            borderColor: 'red'
                        }]
                    },
                    options: {
                        responsive: false,
                        scales: {
                            x: {
                                title: {
                                    display: true,
                                    text: 'Time [s]'
                                }
                            },
                            y: {
                                min: ((graph_voltage_range * (-1)) + graph_dc_offset),
                                max: (graph_voltage_range + graph_dc_offset)
                            }
                        },
                        animation: {
                            duration: 0
                        },
                        hover: {
                            animationDuration: 0
                        },
                        responsiveAnimationDuration: 0
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
    });
}

initializeChart();
updateButtonText();
