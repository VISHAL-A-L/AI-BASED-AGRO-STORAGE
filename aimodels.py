import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import IsolationForest

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# Load dataset
def load_data():

    try:
        data = pd.read_csv("sensor_data.csv")
    except:
        data = pd.DataFrame(columns=["temperature","humidity","gas"])

    return data


# ---------------- Random Forest ----------------

def train_random_forest(data):

    if len(data) < 20:
        return None

    X = data[['temperature','humidity','gas']]

    y = []

    for i in range(len(data)):

        if data['temperature'][i] > 30 or data['humidity'][i] > 75 or data['gas'][i] > 350:
            y.append(1)
        else:
            y.append(0)

    model = RandomForestClassifier()

    model.fit(X,y)

    return model


# ---------------- Isolation Forest ----------------

def train_isolation_forest(data):

    if len(data) < 20:
        return None

    X = data[['temperature','humidity','gas']]

    model = IsolationForest(contamination=0.1)

    model.fit(X)

    return model


# ---------------- LSTM Model ----------------

def train_lstm(data):

    if len(data) < 30:
        return None

    X = data[['temperature','humidity','gas']].values

    seq = 10

    X_train=[]
    y_train=[]

    for i in range(len(X)-seq):

        X_train.append(X[i:i+seq])

        if X[i+seq][2] > 350:
            y_train.append(1)
        else:
            y_train.append(0)

    X_train=np.array(X_train)
    y_train=np.array(y_train)

    model=Sequential()

    model.add(LSTM(64,return_sequences=True,input_shape=(seq,3)))
    model.add(LSTM(32))
    model.add(Dense(1,activation='sigmoid'))

    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )

    model.fit(X_train,y_train,epochs=10,verbose=0)

    return model