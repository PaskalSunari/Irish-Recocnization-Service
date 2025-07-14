from flask import Flask, jsonify, request, Response
import requests
import os
from flask_cors import CORS
import winreg

app = Flask(__name__)
CORS(app)

def get_device_ip_from_registry():
    try:
        registry_path = r"SOFTWARE\IrishMiddleware"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, "DeviceIP")
            return value
    except Exception as e:
        print(f"Error reading DeviceIP from registry: {e}")
        return None

DEVICE_IP = get_device_ip_from_registry() or "192.168.1.83"  # fallback if not set

LOCK_URL = f"http://{DEVICE_IP}:9980/1.0/lock"
USER_URL = f"http://{DEVICE_IP}:9980/1.0/user"
PROXY_TARGET = "http://server.com:52774"
@app.route('/api/air/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy_air(path):
    url = f"{PROXY_TARGET}/{path}"
    resp = requests.request(
        method=requests.method,
        url=url,
        headers={key: value for key, value in request.headers if key.lower() != 'host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False
    )
    exclude_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in exclude_headers]
    response = Response(resp.content, resp.status_code, headers)
    return response
def get_lock_uid():
    try:
        response = requests.put(LOCK_URL)
        response.raise_for_status()
        data = response.json()
        lock_uid = data.get("lock_uid")
        if lock_uid:
            return jsonify({"lock_uid": lock_uid}), 200
        else:
            return jsonify({"error": "lock_uid not found in response"}), 404
    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching lock UID: {e}"}), 500

@app.route('/user', methods=['GET'])
def get_user():
    lock_uid = request.args.get('lock_uid')
    if not lock_uid:
        return jsonify({"error": "Missing lock_uid parameter"}), 400
    url = f"{USER_URL}?lock_uid={lock_uid}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return jsonify(data), 200
    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching user: {e}"}), 500

@app.route('/user_with_lock', methods=['GET'])
def user_with_lock():
    # Step 1: Get lock_uid
    try:
        lock_response = requests.put(LOCK_URL)
        lock_response.raise_for_status()
        lock_data = lock_response.json()
        lock_uid = lock_data.get("lock_uid")
        if not lock_uid:
            return jsonify({"error": "lock_uid not found in response"}), 404
    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching lock UID: {e}"}), 500

    # Step 2: Use lock_uid to get user data
    user_url = f"{USER_URL}?lock_uid={lock_uid}"
    try:
        user_response = requests.get(user_url)
        user_response.raise_for_status()
        user_data = user_response.json()
        return jsonify(user_data), 200
    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching user: {e}"}), 500

@app.route('/userlist', methods=['GET'])
def get_user_list():
    return user_with_lock()

@app.route('/', methods=['GET'])
def root_user_with_lock():
    return user_with_lock()
@app.route('/Camera', methods=['GET'])
def get_camera():
    try:
        lock_response = requests.put(LOCK_URL)
        lock_response.raise_for_status()
        lock_data = lock_response.json()
        lock_uid = lock_data.get("lock_uid")
        if not lock_uid:
            return jsonify({"error": f"lock_uid not found in response"}), 404
    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching lock UID: {e}"}), 500
    camera_url = f"http://{DEVICE_IP}:9980/1.0/camera?lock_uid={lock_uid}"
    try:
        camera_response = requests.get(camera_url)
        camera_response.raise_for_status()
        camera_data = camera_response.json()
        return jsonify(camera_data), 200
    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching camera: {e}"}), 500
@app.route('/CameraControl', methods=['GET','POST'])
def camera_control():
    try:
        lock_response = requests.put(LOCK_URL)
        lock_response.raise_for_status()
        lock_data = lock_response.json()
        lock_uid = lock_data.get("lock_uid")
        if not lock_uid:
            return jsonify({"error": f"lock_uid not found in response"}), 404
    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching lock UID: {e}"}), 500
    control_url = (
        f"http://{DEVICE_IP}:9980/1.0/camera/control/start?"
        f"lock_uid={lock_uid}&face_mode=true&glasses_mode=false&both_eye_mode=false&either_eye_mode=true"
    )
    try:
        control_response = requests.post(control_url)
        control_response.raise_for_status()
        control_data = control_response.json()
        return jsonify(control_data), 200
    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching camera control: {e}"}), 500
@app.route('/SlaveMode', methods=['GET','POST'])
def slave_mode():    
    try:
        print(f"Sending post request to Paskal ")
        lock_response = requests.put(LOCK_URL)
        lock_response.raise_for_status()
        lock_data = lock_response.json()
        lock_uid = lock_data.get("lock_uid")
        if not lock_uid:
            return jsonify({"error": f"lock_uid not found in response"}), 404
    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching lock UID: {e}"}), 500
    slave_url = f"http://{DEVICE_IP}:9980/1.0/camera?lock_uid={lock_uid}"
    payload = {
        "serial_number": "OA1405A031576",  # Use the correct serial number for your device
        "camera_mode": "Slave",
        "audio_enabled": True
    }
    headers = {
          "Content-Type": "application/json"
    }
    try:       
        slave_response = requests.post(slave_url, headers=headers, json=payload) 
        slave_response.raise_for_status()
        slave_data = slave_response.json()
        return jsonify(slave_data), 200
    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching slave mode: {e}"}), 500
    
@app.route('/RecogMode', methods=['GET','POST'])
def recog_mode():
    try:
        lock_response = requests.put(LOCK_URL)
        lock_response.raise_for_status()
        lock_data = lock_response.json()
        lock_uid = lock_data.get("lock_uid")
        if not lock_uid:
            return jsonify({"error": f"lock_uid not found in response"}), 404
    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching lock UID: {e}"}), 500
    recog_url = f"http://{DEVICE_IP}:9980/1.0/camera?lock_uid={lock_uid}"
    try:
        recog_response = requests.post(recog_url)
        recog_response.raise_for_status()
        recog_data = recog_response.json()
        return jsonify(recog_data), 200
    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching recog mode: {e}"}), 500
    
@app.route('/StartCamera', methods=['GET','POST'])
def start_camera():   
    try:
        print(f"Hello durgen dai")
        lock_response = requests.put(LOCK_URL)
        lock_response.raise_for_status()
        lock_data = lock_response.json()
        lock_uid = lock_data.get("lock_uid")
        if not lock_uid:
            return jsonify({"error": f"lock_uid not found in response"}), 404
    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching lock UID: {e}"}), 500
    start_url = f"http://{DEVICE_IP}:9980/1.0/camera/control/start?lock_uid={lock_uid}&face_mode=true&glasses_mode=false&both_eye_mode=false&either_eye_mode=true"
    print(f"Sending POST request to {start_url}")
    try:
        camera_response = requests.post(start_url)
        camera_response.raise_for_status()
        camera_data = camera_response.json()
        return jsonify(camera_data), 200
    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching start camera: {e}"}), 500
    
@app.route('/StopCamera', methods=['GET','POST'])
def stop_camera():
    print(f"break point Status code---")
    try:
        lock_response = requests.put(LOCK_URL)
        lock_response.raise_for_status()
        lock_data = lock_response.json()
        lock_uid = lock_data.get("lock_uid")
        if not lock_uid:
            return jsonify({"error": f"lock_uid not found in response"}), 404
    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching lock UID: {e}"}), 500
    stop_url = f"http://{DEVICE_IP}:9980/1.0/camera/control/stop?lock_uid={lock_uid}"
    try:
        print(f"Sending GET request to {stop_url}") 
        stop_response = requests.post(stop_url)
        stop_response.raise_for_status()
        stop_data = stop_response.json()              
        print(f"GET request sent. Status code: {stop_response.status_code}")
        print(f"Response headers: {stop_response.headers}")
        print(f"Response body: {stop_response.text}")
        return jsonify(stop_data), 200
    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching stop camera: {e}"}), 500
@app.route('/MatchData', methods=['GET','POST'])
def match_data():
    try:
        lock_response = requests.put(LOCK_URL)
        lock_response.raise_for_status()
        lock_data = lock_response.json()
        lock_uid = lock_data.get("lock_uid")
        if not lock_uid:
            return jsonify({"error": f"lock_uid not found in response"}), 404
    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching lock UID: {e}"}), 500
    match_url = f"http://{DEVICE_IP}:9980/1.0/match-data/38118632-534a-11f0-aa39-503f98007277?lock_uid={lock_uid}"
    try:
        match_response = requests.get(match_url)
        match_response.raise_for_status()
        match_data = match_response.json()
        return jsonify(match_data), 200
    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching match data: {e}"}), 500
@app.route('/LastUserDetail', methods=['GET'])
def last_user_detail():
    try:
        lock_response = requests.put(LOCK_URL)
        lock_response.raise_for_status()
        lock_data = lock_response.json()
        lock_uid = lock_data.get("lock_uid")
        if not lock_uid:
            return jsonify({"error": f"lock_uid not found in response"}), 404
    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching lock UID: {e}"}), 500
    match_url = f"http://{DEVICE_IP}:9980/1.0/match-data/38118632-534a-11f0-aa39-503f98007277?lock_uid={lock_uid}"
    try:
        match_response = requests.get(match_url)
        match_response.raise_for_status()
        match_data = match_response.json()
        items = match_data.get("items", [])
        if not items:
            return jsonify({"error": "No items found in match data"}), 404
        last_user = items[-1]
        return jsonify(last_user), 200
    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching last user detail: {e}"}), 500 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
