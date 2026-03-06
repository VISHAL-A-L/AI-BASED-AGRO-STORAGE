from flask import Flask, request, jsonify, send_file
import pandas as pd

app = Flask(__name__)

file = "sensor_data.csv"

# Load old data if exists
try:
    data = pd.read_csv(file)

    if "motion" not in data.columns:
        data["motion"] = 0

except:
    data = pd.DataFrame(columns=["temperature","humidity","gas","motion"])


# ---------------- HOME PAGE ----------------

@app.route('/')
def home():
    return send_file("dashboard.html")


# ---------------- RECEIVE SENSOR DATA ----------------

@app.route('/data', methods=['POST'])
def receive():

    global data

    sensor = request.get_json()

    if not sensor:
        return jsonify({"error":"No data received"}),400

    temp = sensor.get("temperature",0)
    hum = sensor.get("humidity",0)
    gas = sensor.get("gas",0)
    motion = sensor.get("motion",0)

    print("\n===== SENSOR DATA RECEIVED =====")
    print("Temperature :", temp)
    print("Humidity    :", hum)
    print("Gas         :", gas)
    print("Motion      :", motion)
    print("================================\n")

    new_row = {
        "temperature": temp,
        "humidity": hum,
        "gas": gas,
        "motion": motion
    }

    data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)

    data.to_csv(file, index=False)

    print("Total rows stored:", len(data))

    return jsonify({"status":"data stored"})


# ---------------- SEND DATA TO DASHBOARD ----------------

@app.route('/getdata')
def getdata():

    if len(data) == 0:

        return jsonify({
            "temperature":0,
            "humidity":0,
            "gas":0,
            "motion":0,
            "rf_prediction":"No Data",
            "iso_prediction":"No Data",
            "lstm_prediction":"No Data"
        })

    last = data.iloc[-1]

    return jsonify({

        "temperature": float(last["temperature"]),
        "humidity": float(last["humidity"]),
        "gas": float(last["gas"]),
        "motion": int(last["motion"]),

        "rf_prediction":"Running",
        "iso_prediction":"Running",
        "lstm_prediction":"Running"
    })


# ---------------- VIEW STORED DATA ----------------

@app.route('/view')
def view():

    return data.to_html()


# ---------------- DOWNLOAD CSV ----------------

@app.route('/download')
def download():

    return send_file(
        file,
        mimetype="text/csv",
        as_attachment=True,
        download_name="onion_storage_data.csv"
    )


app.run(host="0.0.0.0", port=5000)