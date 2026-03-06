from flask import Flask, request, jsonify
import pandas as pd
import numpy as np

app = Flask(__name__)

file = "sensor_data.csv"

try:
    df = pd.read_csv(file)
except:
    df = pd.DataFrame(columns=["temperature","humidity","gas"])

@app.route('/data', methods=['POST'])
def receive():

    sensor = request.form['sensor']
    t,h,g = sensor.split(",")

    t=float(t)
    h=float(h)
    g=float(g)

    new_row = {"temperature":t,"humidity":h,"gas":g}

    global df
    df = pd.concat([df,pd.DataFrame([new_row])],ignore_index=True)

    df.to_csv(file,index=False)

    return "ok"

app.run(host="0.0.0.0",port=5000)