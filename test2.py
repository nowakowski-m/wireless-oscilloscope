from flask import Flask, render_template, Response
import time
import numpy as np
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from scipy.fft import fft

app = Flask(__name__)

# Initializing I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Setting data rate
ads_data_rate = 250

# Initializing ADS1115
ads = ADS.ADS1115(i2c, data_rate=ads_data_rate)

# Setting measure channel ADC (AI1)
chan = AnalogIn(ads, ADS.P1)

# Frequency of reading data by app
frequency = 1 / ads_data_rate

# Constant value to convert data from bites to volts
VOLTAGE_REFERENCE = 4.096  # For ADS1115 using GAIN=1

# Empty list for storing data.
data_points = []

# Frequency to analyze with FFT
target_frequency = 50  # Hz

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/graph')
def graph():
    return render_template('graph.html')

@app.route('/data')
def data():
    def generate():
        while True:
            # Reading raw value from ADC
            raw_value = chan.value

            # Converting data to volts
            voltage = (raw_value / 65535) * VOLTAGE_REFERENCE  # 65535 is max bit value of ADC data

            # Adding data to list
            data_points.append(voltage)

            if len(data_points) > 100:
                # If list contain 100 points, delete last one, to leave it always with 100 only
                data_points.pop(0)

            # Converting data to proper format for app
            data_string = f"data: {','.join(map(str, data_points))}\n\n"

            # Perform FFT analysis
            fft_result = fft(data_points)
            fft_freq = np.fft.fftfreq(len(data_points), d=frequency)
            target_freq_index = np.abs(fft_freq - target_frequency).argmin()
            target_freq_amplitude = np.abs(fft_result[target_freq_index])
            
            # Print the amplitude of the target frequency
            print(f"Amplitude of {target_frequency} Hz: {target_freq_amplitude}")

            yield data_string
            time.sleep(frequency)

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
