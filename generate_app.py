from flask import Flask, render_template, session, Response, request, redirect, url_for
import numpy as np
from threading import Thread
import time

app = Flask(__name__)
app.secret_key = 'test'

# Prepare for creating graph.
x_data = []
y_data = []
frequency = 0.1
reading_pause = False

def read_session_value(obj: str, default: bool):
    with app.test_request_context():
        return session.get(obj, default)

# Temp. function for generating data - instead of using real one.
def generate_data():
    global x_data, y_data
    while True:
        # Simunation of real data.
        x = np.linspace(0, 5, 100)
        y = np.sin(x + time.time()) / 4
        
        # Assigning data to earlier created lists.
        x_data = x
        y_data = y
        
        # Waiting for next generate.
        time.sleep(frequency)

# Thread to generate data.
data_thread = Thread(target=generate_data)
data_thread.daemon = True
data_thread.start()

# Route to main page.
@app.route('/')
def index():
    return render_template('index.html')

# Route to graph page.
@app.route('/graph')
def inna_strona():
    return render_template('graph.html')

@app.route('/data')
def data():
    def generate():
        read_session_value('flag', False)
        while not reading_pause:
                # Converting data to proper data format.
            yield f"data: {','.join(map(str, x_data))}\n"
            yield f"data: {','.join(map(str, y_data))}\n\n"
            time.sleep(frequency)

    return Response(generate(), mimetype='text/event-stream')

@app.route('/toggle_flag', methods=['POST'])
def toggle_flag():
    session['flag'] = not session.get('flag', False)
    global reading_pause
    reading_pause = session['flag']
    return Response('')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)