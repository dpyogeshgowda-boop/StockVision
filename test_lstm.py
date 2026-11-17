from backend.models.lstm_model import train_lstm_model

print("Starting TCS LSTM training...")

result = train_lstm_model("TCS")

print("\nLSTM MODEL RESULTS")
print("========================")

for key, value in result.items():
    print(f"{key}: {value}")