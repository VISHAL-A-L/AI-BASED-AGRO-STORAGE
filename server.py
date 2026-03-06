from flask import Flask, request, jsonify, send_file
import pandas as pd
from datetime import datetime
import numpy as np
import os
import joblib
from tensorflow.keras.models import load_model

app = Flask(__name__)

file = "sensor_data.csv"

# ---------------- LOAD AI MODELS ----------------

try:
    rf_model = joblib.load("rf_model.pkl")
    iso_model = joblib.load("iso_model.pkl")
    lstm_model = load_model("onion_lstm_model.h5")
    print("AI Models Loaded")
except:
    rf_model = None
    iso_model = None
    lstm_model = None
    print("AI Models Not Found")

# ---------------- CREATE CSV FILE ----------------

if not os.path.exists(file):

    data = pd.DataFrame(columns=[
        "date",
        "time",
        "temperature",
        "humidity",
        "gas",
        "motion"
    ])

    data.to_csv(file, index=False)

# ---------------- LOAD DATA ----------------

data = pd.read_csv(file)

# ---------------- HOME PAGE ----------------

@app.route('/')
def home():
    return send_file("dashboard.html")

# ---------------- RECEIVE ESP DATA ----------------

@app.route('/data', methods=['POST'])
def receive():

    global data

    sensor = request.get_json()

    if not sensor:
        return jsonify({"error": "No data received"}), 400

    temp = sensor.get("temperature", 0)
    hum = sensor.get("humidity", 0)
    gas = sensor.get("gas", 0)
    motion = sensor.get("motion", 0)

    now = datetime.now()

    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    new_row = {
        "date": date,
        "time": time,
        "temperature": temp,
        "humidity": hum,
        "gas": gas,
        "motion": motion
    }

    data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)

    data.to_csv(file, index=False)

    return jsonify({"status": "stored"})

# ---------------- SEND DATA TO DASHBOARD ----------------

@app.route('/getdata')
def getdata():

    if len(data) == 0:

        return jsonify({
            "temperature": 0,
            "humidity": 0,
            "gas": 0,
            "motion": 0,
            "rf_prediction": "Waiting",
            "iso_prediction": "Waiting",
            "lstm_prediction": "Waiting"
        })

    last = data.iloc[-1]

    temp = float(last["temperature"])
    hum = float(last["humidity"])
    gas = float(last["gas"])
    motion = int(last["motion"])

    # IMPORTANT → same features as AI model
    features = np.array([[temp, hum, gas, motion]])

    # ---------- RANDOM FOREST ----------

    try:
        rf_pred = rf_model.predict(features)[0]
        rf = "Spoilage Risk" if rf_pred == 1 else "Storage Safe"
    except:
        rf = "RF Error"

    # ---------- ISOLATION FOREST ----------

    try:
        iso_pred = iso_model.predict(features)[0]
        iso = "Anomaly Detected" if iso_pred == -1 else "Normal"
    except:
        iso = "ISO Error"

    # ---------- LSTM MODEL ----------

    try:

        if len(data) >= 5:

            seq = data[["temperature","humidity","gas","motion"]].tail(5).values
            seq = seq.reshape((1,5,4))

            pred = lstm_model.predict(seq)

            lstm = "Future Spoilage Risk" if pred[0][0] > 0.5 else "Stable"

        else:

            lstm = "Collecting Data"

    except:

        lstm = "LSTM Error"

    return jsonify({

        "temperature": temp,
        "humidity": hum,
        "gas": gas,
        "motion": motion,

        "rf_prediction": rf,
        "iso_prediction": iso,
        "lstm_prediction": lstm

    })

# ---------------- VIEW DATA ----------------

@app.route('/view')
def view():
    return data.to_html()

# ---------------- DOWNLOAD EXCEL ----------------

@app.route('/download')
def download():

    return send_file(
        file,
        mimetype="text/csv",
        as_attachment=True,
        download_name="onion_storage_data.csv"
    )

# ---------------- RUN SERVER ----------------

app.run(host="0.0.0.0", port=5000)