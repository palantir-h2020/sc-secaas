from flask import Flask, request, jsonify
import subprocess
import time
import psutil
app = Flask(__name__)


@app.route("/start-ntopng", methods=['POST'])
def start_ntopng():
    try:
        data = request.get_json()
        id_interface = data['id_interface']
        ntopng_data_path = data['ntopng_data_path']

        subprocess.Popen(['ntopng', '-i', id_interface, '-d' ,ntopng_data_path])
        time.sleep(1)
        response = {'output': 'Ntopng started successfully'}
        return jsonify(response)
    
    except Exception as e:
        print({e})

@app.route("/stop-ntopng", methods=['GET'])
def stop_ntopng():
    try:
        for process in psutil.process_iter():
            if "ntopng" in process.name() and "zombie" not in process.status():
                process.kill()
        
        time.sleep(1)
        response = {'output': 'Ntopng stopped successfully'}
        return jsonify(response)
    except Exception as e:
        print({e})


if __name__ == "__main__":
    app.run(port=5001)
