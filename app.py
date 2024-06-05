from flask import Flask, render_template, Response, session, jsonify, request
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

app = Flask(__name__)
app.secret_key = 'test'

i2c = busio.I2C(board.SCL, board.SDA)

ads_data_rate = 860
ads = ADS.ADS1115(i2c, data_rate=ads_data_rate, gain=1)
chan = AnalogIn(ads, ADS.P1)
freq = 10
period = (1 / (ads_data_rate / (freq / 5)))

is_generating = True
VOLTAGE_REFERENCE = 4.096

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


@app.route('/data')
def data():
    def generate():
        while is_generating:
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
    global is_generating
    is_generating = not is_generating
    return jsonify(success=True)


@app.route('/get_flag_status', methods=['GET'])
def get_flag_status():
    return jsonify(isGenerating=is_generating)


@app.route('/sampling-period')
def get_sampling_period():
    data = {
        'sampling_period': period,
        'points_amount': graph_points_amount
    }
    return jsonify(data)


@app.route('/set_frequency', methods=['POST'])
def set_frequency():
    data = request.get_json()
    session['frequency'] = float(data['frequency'])
    global period
    period = 1 / (ads_data_rate / (session['frequency'] / 5))
    return jsonify({'status': 'success', 'frequency': session['frequency']})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
