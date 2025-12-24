from flask import Flask, jsonify, request, Response
import requests
import os
from flask_cors import CORS
import winreg
import base64
import re

app = Flask(__name__)
CORS(app)

def get_device_ip_from_registry():
    try:
        registry_path = r"SOFTWARE\WOW6432Node\IrishMiddleware"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, "DeviceIP")
            return value
    except Exception as e:
        print(f"Error reading DeviceIP from registry: {e}")
        return None

DEVICE_IP = get_device_ip_from_registry()   # fallback if not set

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
        lock_response = requests.put(LOCK_URL)
        lock_response.raise_for_status()
        lock_data = lock_response.json()
        lock_uid = lock_data.get("lock_uid")
        if not lock_uid:
            return jsonify({"error": f"lock_uid not found in response"}), 404
    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching lock UID: {e}"}), 500
    start_url = f"http://{DEVICE_IP}:9980/1.0/camera/control/start?lock_uid={lock_uid}&face_mode=true&glasses_mode=false&both_eye_mode=false&either_eye_mode=true"
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
def read_registry():
    base_path = r"Software\SP\License\IRIS"

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, base_path, 0, winreg.KEY_READ)
    except FileNotFoundError:
        return jsonify(
            
            data = {
        "licenseKey": "",
        "mac": ""
    }
        )

    try:
        type_ = winreg.QueryValueEx(key, "Type")[0]
        code = winreg.QueryValueEx(key, "Code")[0]
        license_key = winreg.QueryValueEx(key, "LicenseKey")[0]
        mac = winreg.QueryValueEx(key, "MAC")[0]
        ip = winreg.QueryValueEx(key, "IP")[0]
        computer_name = winreg.QueryValueEx(key, "ComputerName")[0]
    except FileNotFoundError:
        # If any key does not exist
        type_ = code = license_key = mac = ip = computer_name = None

    winreg.CloseKey(key)

    data = {
        "licenseKey": license_key,
        "mac": mac
    }

    return jsonify(data)
    
def clean_string(s):
    s = s.replace('\r', '')
    s = s.replace('\n', '')
    s = re.sub(r'\\(?![\\rntbfv\"\'\\/])', '', s)
    return s

def fix_base64_padding(b64_str):
    missing_padding = len(b64_str) % 4
    if missing_padding:
        b64_str += '=' * (4 - missing_padding)
    return b64_str

@app.route('/LivePreview', methods=['GET'])
def live_face_preview():
    try:
        lock_response = requests.put(LOCK_URL)
        lock_response.raise_for_status()
        lock_data = lock_response.json()
        lock_uid = lock_data.get("lock_uid")
        if not lock_uid:
            return jsonify({"error": "lock_uid not found in response"}), 404
    except requests.RequestException as e:
        return jsonify({"error": f"Error in fetching lock UID: {e}"}), 500

    face_url = f"http://{DEVICE_IP}:9980/1.0/preview?lock_uid={lock_uid}"
    try:
        face_response = requests.get(face_url)
        face_response.raise_for_status()
        if face_response.status_code == 204 or not face_response.text.strip():
            return jsonify({"error": "No content returned from device (204 No Content)"}), 204

        # Get the device response and extract the base64 string from "face_image"
        face_data = face_response.json()
        base64_str = face_data.get("face_image")
        if not base64_str:
            return jsonify({"error": "No base64 image data found in device response"}), 404

        # Clean, fix, decode, and re-encode
        cleaned = clean_string(base64_str)
        fixed = fix_base64_padding(cleaned)
        decoded_bytes = base64.b64decode(fixed)
        # Optionally save to file
        with open("face.jpg", "wb") as img_file:
            img_file.write(decoded_bytes)
        # Re-encode for frontend
        reencoded_base64 = base64.b64encode(decoded_bytes).decode('utf-8')
        data=read_registry()
        print(data)
        return jsonify({"image_base64": reencoded_base64}), 200

    except requests.RequestException as e:
        return jsonify({"error": f"Error in fetching match data: {e}"}), 500
    except ValueError as ve:
        return jsonify({"error": "Device did not return valid JSON", "content": face_response.text}), 500
    except Exception as e:
        return jsonify({"error": f"Error processing base64 image: {e}"}), 500
        
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
