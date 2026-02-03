from flask import Flask, request, jsonify
from flask_cors import CORS
from model_training import StockPredictionSystem
import os
import numpy as np

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from your extension

# Cache for trained systems
systems_cache = {}

# -----------------------------
# Load valid tickers at startup
# -----------------------------
TICKERS_FILE = os.path.join(os.path.dirname(__file__), "tickers_list.txt")
if not os.path.exists(TICKERS_FILE):
    raise FileNotFoundError("tickers_list.txt not found! Run fetch_tickers.py first.")

with open(TICKERS_FILE) as f:
    VALID_TICKERS = set(line.strip().upper() for line in f)

# -----------------------------
# Helper function to convert NumPy/pandas types to native Python
# -----------------------------
def to_native(x):
    if isinstance(x, (np.ndarray, np.float32, np.float64, np.int32, np.int64)):
        return float(x[0]) if isinstance(x, np.ndarray) else float(x)
    return x

# -----------------------------
# Flask route: get stock info
# -----------------------------
@app.route('/get_stock_info')
def get_stock_info():
    ticker = request.args.get('ticker', '').upper()
    
    # Validate ticker
    if ticker not in VALID_TICKERS:
        return jsonify({"error": f"Invalid ticker: {ticker}"}), 400

    # Initialize or reuse system
    if ticker not in systems_cache:
        try:
            system = StockPredictionSystem(ticker)
            system.initialize()
            systems_cache[ticker] = system
        except Exception as e:
            return jsonify({"error": f"Failed to initialize system: {str(e)}"}), 500
    else:
        system = systems_cache[ticker]

    # Get last row features for prediction
    try:
        last_features = system.processor.data.drop('Close', axis=1).iloc[-1].values
        future_predictions = system.predictor.predict_future(last_features)
        # Convert all NumPy/pandas types to native Python floats
        future_predictions = {k: to_native(v) for k, v in future_predictions.items()}
        latest_price = float(system.processor.data['Close'].iloc[-1])
    except Exception as e:
        return jsonify({"error": f"Failed to predict: {str(e)}"}), 500

    response = {
        "ticker": ticker,
        "price": latest_price,
        "future_predictions": future_predictions
    }

    return jsonify(response)

# -----------------------------
# Run server
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
