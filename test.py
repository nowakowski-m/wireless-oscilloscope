from flask import Flask, render_template, Response, session, jsonify, request
import time
import board  # type: ignore
import busio  # type: ignore
import numpy as np
import adafruit_ads1x15.ads1115 as ADS  # type: ignore
from adafruit_ads1x15.analog_in import AnalogIn  # type: ignore

app = Flask(__name__)
app.secret_key = 'test'

i2c = busio.I2C(board.SCL, board.SDA)

supported_data_rates = [8, 16, 32, 64, 128, 250, 475, 860]


def find_closest_data_rate(frequency):
    # Nyquist theorem: sampling rate should be at least twice the max frequency
    nyquist_rate = 2 * frequency
    closest_rate = min(supported_data_rates, key=lambda x: (x < nyquist_rate, abs(x - nyquist_rate)))
    return closest_rate


def calculate_period(data_rate, freq):
    # Oblicz okres na podstawie data_rate i freq
    return 1 / (data_rate / (freq * 5))


def adjust_frequency(freq):
    global ads_data_rate, period
    ads_data_rate = find_closest_data_rate(freq)
    period = calculate_period(ads_data_rate, freq)


freq = 50  # Replace with the actual frequency of the input signal

adjust_frequency(freq)

ads = ADS.ADS1115(i2c, data_rate=ads_data_rate, gain=1)
chan = AnalogIn(ads, ADS.P1)

period = 1 / (ads_data_rate / (freq / 5))
reading_pause = False
# Constant value to convert data from bites to volts
VOLTAGE_REFERENCE = 4.096  # For ADS1115 using GAIN=1
# ALSO CAN CHANGE GAIN, OR ADD SLIDER FOR IT, IDK IF THIS IS THE SAME AS GAIN

# Empty list for storing data.
data_points = []
graph_points_amount = 102


def read_session_value(obj: str, default: bool):
    with app.test_request_context():
        return session.get(obj, default)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/graph')
def graph():
    return render_template('graph.html')


@app.route('/set_sampling_rate', methods=['POST'])
def set_sampling_rate():
    global ads_data_rate, period
    new_rate = request.json.get('sampling_rate', 860)
    ads.data_rate = new_rate
    period = calculate_period(new_rate, freq)
    return jsonify({'status': 'success', 'new_rate': new_rate, 'new_period': period})


@app.route('/data')
def data():
    def generate():
        while not reading_pause:
            raw_value = chan.value
            voltage = (raw_value / 65535) * 8
            data_points.append(voltage)
            if len(data_points) > graph_points_amount:
                data_points.pop(0)
            data_string = f"data: {','.join(map(str, data_points))}\n\n"
            yield data_string
            time.sleep(period)

    return Response(generate(), mimetype='text/event-stream')


@app.route('/toggle_flag', methods=['POST'])
def toggle_flag():
    session['flag'] = not session.get('flag', False)
    global reading_pause
    reading_pause = session['flag']
    return Response('')


@app.route('/sampling-period')
def get_sampling_period():
    data = {
        'sampling_period': period,
        'points_amount': graph_points_amount
    }

    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
