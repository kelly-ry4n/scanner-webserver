
import webcam
import json
from threading import Lock
from flask import Flask


scan_lock = Lock()


app = Flask(__name__)

@app.route("/start_scan")
def start_scan():
    if scan_lock.acquire(False):
        webcam.new_scan()
        return json.dumps({'scanning':True})
    else:
        return json.dumps({'error':'Scan already in progress, please end before starting a new scan.'})

@app.route("/end_scan")
def end_scan():
    if scan_lock.locked():
        scan_lock.release()
        return json.dumps({'scanning':False})
    else:
        return json.dumps({'error': 'No scan in progress. Cannot end scan.'})

@app.route("/take_img")
def take_img():
    if scan_lock.locked():
        return webcam.take_img()
    else:
        return json.dumps({'error': 'No scan in progress. Cannot take image.'})




if __name__ == "__main__":
    app.debug = True
    app.run()