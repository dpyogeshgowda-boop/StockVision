import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

import joblib

# STEP 1: Load dataset

df = pd.read_csv(
    "nifty50_technical_data.csv",
    header=[0, 1],
    index_col=0
)

df.index = pd.to_datetime(df.index)

# Extract closing prices

prices = df[("Close", "^NSEI")].values.reshape(-1, 1)

print("Total observations:", len(prices))


# STEP 2: Normalize the data

scaler = MinMaxScaler(feature_range=(0, 1))

scaled_data = scaler.fit_transform(prices)

joblib.dump(scaler, "price_scaler.pkl")


# STEP 3: Create sequences

sequence_length = 60

X = []
y = []

for i in range(sequence_length, len(scaled_data)):

    X.append(scaled_data[i-sequence_length:i, 0])

    y.append(scaled_data[i, 0])

X = np.array(X)
y = np.array(y)

X = X.reshape(X.shape[0], X.shape[1], 1)

print("Input shape:", X.shape)
print("Output shape:", y.shape)


# STEP 4: Chronological train-test split

split = int(len(X) * 0.8)

X_train = X[:split]
X_test = X[split:]

y_train = y[:split]
y_test = y[split:]

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))


# STEP 5: Build LSTM model

model = Sequential()

model.add(
    LSTM(
        units=50,
        return_sequences=True,
        input_shape=(X_train.shape[1], 1)
    )
)

model.add(Dropout(0.2))

model.add(
    LSTM(
        units=50,
        return_sequences=False
    )
)

model.add(Dropout(0.2))

model.add(Dense(units=25))

model.add(Dense(units=1))


# STEP 6: Compile model

model.compile(
    optimizer="adam",
    loss="mean_squared_error"
)


# STEP 7: Train model

print("\nTraining LSTM Model...")

history = model.fit(
    X_train,
    y_train,
    epochs=25,
    batch_size=32,
    validation_split=0.1,
    shuffle=False
)


# STEP 8: Predict test data

predictions = model.predict(X_test)

predictions = scaler.inverse_transform(predictions)

actual_prices = scaler.inverse_transform(
    y_test.reshape(-1, 1)
)


# STEP 9: Evaluate model

mae = mean_absolute_error(
    actual_prices,
    predictions
)

rmse = np.sqrt(
    mean_squared_error(actual_prices, predictions)
)

print("\nMODEL PERFORMANCE")

print("MAE:", round(mae, 2))
print("RMSE:", round(rmse, 2))


# STEP 10: Save model

model.save("nifty50_lstm_model.keras")


# STEP 11: Plot actual vs predicted prices

plt.figure(figsize=(12, 6))

plt.plot(
    actual_prices,
    label="Actual Price"
)

plt.plot(
    predictions,
    label="Predicted Price"
)

plt.title("NIFTY 50 - LSTM Price Prediction")

plt.xlabel("Test Trading Days")
plt.ylabel("Closing Price")

plt.legend()
plt.grid()

plt.tight_layout()

plt.savefig("lstm_prediction.png")

plt.show()

print("\nLSTM Model Training Completed!")
print("Model saved successfully!")