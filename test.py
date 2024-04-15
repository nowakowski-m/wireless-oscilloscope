from flask import Flask, render_template, Response
import time
import Adafruit_ADS1x15

app = Flask(__name__)

# Initialize ADC
adc = Adafruit_ADS1x15.ADS1115()
GAIN = 1

# Route to main page.
@app.route('/')
def index():
    return render_template('index.html')

# Route to graph page.
@app.route('/graph')
def graph():
    return render_template('graph.html')

@app.route('/data')
def data():
    def generate():
        while True:
            # Read data from ADC channel 1 (AI1)
            value = adc.read_adc(1, gain=GAIN)
            
            # Convert data to proper format
            data_string = f"data: {value}\n\n"

            yield data_string
            time.sleep(0.1)  # Adjust frequency of data sending

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)