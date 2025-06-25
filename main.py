from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

LOCK_URL = "http://192.168.1.82:9980/1.0/lock"
USER_URL = "http://192.168.1.82:9980/1.0/user"

@app.route('/lock_uid', methods=['GET'])
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

@app.route('/', methods=['GET'])
def root_user_with_lock():
    return user_with_lock()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
