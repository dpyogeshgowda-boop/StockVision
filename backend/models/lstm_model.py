import numpy as np
import pandas as pd

from pathlib import Path

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.regularizers import l2


BASE_DIR = Path(__file__).resolve().parents[2]
STOCK_DIR = BASE_DIR / "data" / "stocks"


def train_lstm_model(symbol="TCS", sequence_length=60):

    symbol = symbol.upper()

    file_path = STOCK_DIR / f"{symbol}.csv"

    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found: {symbol}")

    # --------------------------------
    # 1. LOAD DATA
    # --------------------------------

    df = pd.read_csv(file_path)

    required = ["Close"]

    for col in required:
        if col not in df.columns:
            raise ValueError(f"{col} column not found")

    if "Date" in df.columns:
        dates = pd.to_datetime(
            df["Date"], errors="coerce"
        )
    else:
        dates = pd.Series(
            pd.date_range(
                start="2000-01-01",
                periods=len(df),
                freq="D"
            )
        )

    # Convert available market columns to numeric
    market_columns = [
        "Open", "High", "Low", "Close", "Volume"
    ]

    for col in market_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col], errors="coerce"
            )

    # --------------------------------
    # 2. CREATE TECHNICAL INDICATORS
    # --------------------------------

    df["SMA_20"] = df["Close"].rolling(20).mean()

    df["SMA_50"] = df["Close"].rolling(50).mean()

    delta = df["Close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

    df["RSI_14"] = 100 - (100 / (1 + rs))

    df.loc[
        (avg_loss == 0) & (avg_gain > 0),
        "RSI_14"
    ] = 100

    # --------------------------------
    # 3. SELECT INPUT FEATURES
    # --------------------------------

    features = [
        col for col in market_columns
        if col in df.columns
    ]

    # Volume is optional
    optional_features = [
        "SMA_20",
        "SMA_50",
        "RSI_14"
    ]

    features.extend(optional_features)

    # Remove rows with missing feature values
    df = df.replace([np.inf, -np.inf], np.nan)

    valid = df[features].notna().all(axis=1)
    valid &= dates.notna()

    df = df.loc[valid].copy()

    dates = dates.loc[valid].reset_index(drop=True)

    if len(df) <= sequence_length + 50:
        raise ValueError(
            "Not enough historical data for LSTM training"
        )

    # --------------------------------
    # 4. PREPARE INPUT AND TARGET
    # --------------------------------

    X_values = df[features].values.astype(float)

    y_values = df["Close"].values.reshape(-1, 1)

    split_index = int(len(df) * 0.8)

    # Separate scalers
    feature_scaler = MinMaxScaler()

    target_scaler = MinMaxScaler()

    # Fit only on training data
    feature_scaler.fit(X_values[:split_index])

    target_scaler.fit(y_values[:split_index])

    X_scaled = feature_scaler.transform(X_values)

    y_scaled = target_scaler.transform(y_values)

    # --------------------------------
    # 5. CREATE SEQUENCES
    # --------------------------------

    X = []
    y = []

    for i in range(sequence_length, len(df)):

        X.append(
            X_scaled[i-sequence_length:i]
        )

        y.append(
            y_scaled[i, 0]
        )

    X = np.array(X)
    y = np.array(y)

    # --------------------------------
    # 6. TRAIN-TEST SPLIT
    # --------------------------------

    train_size = split_index - sequence_length

    X_train = X[:train_size]
    X_test = X[train_size:]

    y_train = y[:train_size]
    y_test = y[train_size:]

    if len(X_train) == 0 or len(X_test) == 0:
        raise ValueError(
            "Insufficient training or testing data"
        )

    # --------------------------------
    # 7. BUILD MULTIVARIATE LSTM
    # --------------------------------

    model = Sequential([

        Input(
            shape=(sequence_length, X.shape[2])
        ),

        LSTM(
            64,
            return_sequences=True,
            kernel_regularizer=l2(0.001)
        ),

        Dropout(0.2),

        LSTM(
            32,
            return_sequences=False,
            kernel_regularizer=l2(0.001)
        ),

        Dropout(0.2),

        Dense(16, activation="relu"),

        Dense(1)

    ])

    model.compile(
        optimizer="adam",
        loss="mean_squared_error"
    )

    # --------------------------------
    # 8. TRAIN MODEL
    # --------------------------------

    early_stopping = EarlyStopping(
        monitor="val_loss",
        patience=7,
        restore_best_weights=True
    )

    history = model.fit(
        X_train,
        y_train,
        epochs=50,
        batch_size=32,
        validation_split=0.1,
        callbacks=[early_stopping],
        shuffle=False,
        verbose=1
    )

    # --------------------------------
    # 9. PREDICT TEST DATA
    # --------------------------------

    predictions_scaled = model.predict(
        X_test,
        verbose=0
    )

    predictions = target_scaler.inverse_transform(
        predictions_scaled
    ).flatten()

    actual_prices = target_scaler.inverse_transform(
        y_test.reshape(-1, 1)
    ).flatten()

    # --------------------------------
    # 10. MODEL EVALUATION
    # --------------------------------

    mae = mean_absolute_error(
        actual_prices,
        predictions
    )

    rmse = np.sqrt(
        mean_squared_error(
            actual_prices,
            predictions
        )
    )

    nonzero = actual_prices != 0

    if np.any(nonzero):

        mape = np.mean(
            np.abs(
                (actual_prices[nonzero] - predictions[nonzero])
                / actual_prices[nonzero]
            )
        ) * 100

    else:
        mape = 0

    # --------------------------------
    # 11. DIRECTIONAL ACCURACY
    # --------------------------------

    # Compare each prediction with the previous
    # actual closing price, not the previous prediction.

    original_indices = np.arange(
        split_index,
        len(df)
    )

    previous_actual = df["Close"].values[
        original_indices - 1
    ]

    actual_direction = np.sign(
        actual_prices - previous_actual
    )

    predicted_direction = np.sign(
        predictions - previous_actual
    )

    directional_accuracy = np.mean(
        actual_direction == predicted_direction
    ) * 100

    # --------------------------------
    # 12. ACTUAL VS PREDICTED DATA
    # --------------------------------

    evaluation_data = []

    for i in range(len(actual_prices)):

        evaluation_data.append({

            "date": dates.iloc[original_indices[i]].strftime(
                "%Y-%m-%d"
            ),

            "actual_price": round(
                float(actual_prices[i]), 2
            ),

            "predicted_price": round(
                float(predictions[i]), 2
            )

        })

    evaluation_data = evaluation_data[-250:]

    # --------------------------------
    # 13. NEXT DAY PREDICTION
    # --------------------------------

    last_sequence = X_scaled[-sequence_length:]

    last_sequence = last_sequence.reshape(
        1,
        sequence_length,
        X.shape[2]
    )

    next_scaled = model.predict(
        last_sequence,
        verbose=0
    )

    next_price = target_scaler.inverse_transform(
        next_scaled
    )[0][0]

    latest_actual_price = float(
        df["Close"].iloc[-1]
    )

    expected_change = (
        (next_price - latest_actual_price)
        / latest_actual_price
    ) * 100

    # --------------------------------
    # 14. RETURN RESULTS
    # --------------------------------

    return {

        "symbol": symbol,

        "latest_actual_price": round(
            latest_actual_price, 2
        ),

        "predicted_next_price": round(
            float(next_price), 2
        ),

        "expected_change_percent": round(
            float(expected_change), 2
        ),

        "mae": round(float(mae), 2),

        "rmse": round(float(rmse), 2),

        "mape": round(float(mape), 2),

        "directional_accuracy_percent": round(
            float(directional_accuracy), 2
        ),

        "training_records": int(len(X_train)),

        "testing_records": int(len(X_test)),

        "epochs_completed": len(
            history.history["loss"]
        ),

        "evaluation_data": evaluation_data,

        "model_information": {

            "algorithm": "Multivariate LSTM",

            "model_type": "Deep Learning",

            "input_features": features,

            "sequence_length": sequence_length,

            "training_split": "80%",

            "testing_split": "20%",

            "optimizer": "Adam",

            "loss_function": "Mean Squared Error"

        },

        "disclaimer": (
            "Predictions are estimates based on historical market "
            "data and are not guaranteed future prices or "
            "investment recommendations."
        )

    }