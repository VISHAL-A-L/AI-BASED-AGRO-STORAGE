import pandas as pd
import numpy as np
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# ---------------- LOAD DATA ----------------

data = pd.read_csv("sensor_data.csv")

# use only sensor columns
X = data[["temperature","humidity","gas","motion"]]

# create simple spoilage label
data["label"] = np.where(
    (data["temperature"] > 35) | (data["gas"] > 300),
    1,0
)

y = data["label"]

# ---------------- RANDOM FOREST ----------------

rf = RandomForestClassifier()

rf.fit(X,y)

joblib.dump(rf,"rf_model.pkl")

print("Random Forest trained and saved")

# ---------------- ISOLATION FOREST ----------------

iso = IsolationForest(contamination=0.1)

iso.fit(X)

joblib.dump(iso,"iso_model.pkl")

print("Isolation Forest trained and saved")

# ---------------- LSTM TRAINING ----------------

sequence_length = 5

dataset = data[["temperature","humidity","gas","motion"]].values

X_lstm=[]
y_lstm=[]

for i in range(len(dataset)-sequence_length):

    X_lstm.append(dataset[i:i+sequence_length])
    y_lstm.append(data["label"].iloc[i+sequence_length])

X_lstm=np.array(X_lstm)
y_lstm=np.array(y_lstm)

# ---------------- BUILD LSTM MODEL ----------------

model = Sequential()

model.add(LSTM(64,input_shape=(sequence_length,4)))

model.add(Dense(1,activation="sigmoid"))

model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

model.fit(X_lstm,y_lstm,epochs=10,batch_size=16)

model.save("onion_lstm_model.h5")

print("LSTM model trained and saved")