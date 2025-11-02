from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime

app = Flask(__name__)
model = joblib.load("rf_volatility_model.pkl")

FEATURE_NAMES = ["Open", "High", "Low", "Close", "Volume", "Gold_Close"]
FEATURE_IMPORTANCE = model.feature_importances_

MODEL_INFO = {
    "algorithm": "Random Forest Classifier",
    "n_estimators": 100,
    "features_count": 6,
    "accuracy": 0.5345,
    "f1_score": 0.5248
}

def calculate_technical_indicators(stock_data):
    df = stock_data.copy()
    df = df.sort_values("Date")
    df["MA_5"] = df["Close"].rolling(window=5).mean()
    df["MA_20"] = df["Close"].rolling(window=20).mean()
    df["ROC"] = df["Close"].pct_change(periods=5) * 100
    df["Price_Range"] = df["High"] - df["Low"]
    df["Volume_Change"] = df["Volume"].pct_change() * 100
    latest = df.iloc[-1]
    return {
        "ma_5": float(latest["MA_5"]) if not pd.isna(latest["MA_5"]) else None,
        "ma_20": float(latest["MA_20"]) if not pd.isna(latest["MA_20"]) else None,
        "roc": float(latest["ROC"]) if not pd.isna(latest["ROC"]) else None,
        "price_range": float(latest["Price_Range"]),
        "volume_change": float(latest["Volume_Change"]) if not pd.isna(latest["Volume_Change"]) else None,
        "trend": "Bullish" if latest["MA_5"] > latest["MA_20"] else "Bearish" if not pd.isna(latest["MA_5"]) and not pd.isna(latest["MA_20"]) else "Neutral"
    }

def get_latest_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        stock_data = stock.history(period="90d")
        if stock_data.empty:
            return None, "No data found for this ticker"
        stock_data.reset_index(inplace=True)
        latest_stock = stock_data.iloc[-1]
        gold = yf.Ticker("GC=F")
        gold_data = gold.history(period="90d")
        gold_data.reset_index(inplace=True)
        latest_date = latest_stock["Date"]
        gold_row = gold_data[gold_data["Date"] == latest_date]
        if gold_row.empty:
            gold_value = gold_data.iloc[-1]["Close"]
        else:
            gold_value = gold_row.iloc[0]["Close"]
        tech_indicators = calculate_technical_indicators(stock_data)
        returns = stock_data["Close"].pct_change()
        historical_volatility = returns.std() * np.sqrt(252)
        return {
            "ticker": ticker,
            "date": latest_date.strftime("%Y-%m-%d"),
            "open": float(latest_stock["Open"]),
            "high": float(latest_stock["High"]),
            "low": float(latest_stock["Low"]),
            "close": float(latest_stock["Close"]),
            "volume": float(latest_stock["Volume"]),
            "gold_close": float(gold_value),
            "technical_indicators": tech_indicators,
            "historical_volatility": float(historical_volatility),
            "price_change_pct": float((latest_stock["Close"] - latest_stock["Open"]) / latest_stock["Open"] * 100)
        }, None
    except Exception as e:
        return None, str(e)

def predict_volatility(data):
    feature_vector = np.array([[
        data["open"], data["high"], data["low"], 
        data["close"], data["volume"], data["gold_close"]
    ]])
    prediction = model.predict(feature_vector)[0]
    probabilities = model.predict_proba(feature_vector)[0]
    labels = {0: "Low", 1: "Medium", 2: "High"}
    confidence = float(max(probabilities))
    return {
        "prediction": labels[prediction],
        "prediction_code": int(prediction),
        "confidence": confidence,
        "probabilities": {
            "low": float(probabilities[0]),
            "medium": float(probabilities[1]),
            "high": float(probabilities[2])
        }
    }

def get_feature_contributions(data):
    feature_values = [data["open"], data["high"], data["low"], data["close"], data["volume"], data["gold_close"]]
    normalized_contributions = []
    for i, (name, value, importance) in enumerate(zip(FEATURE_NAMES, feature_values, FEATURE_IMPORTANCE)):
        normalized_contributions.append({
            "name": name,
            "value": value,
            "importance": float(importance),
            "contribution": float(importance * 100)
        })
    normalized_contributions.sort(key=lambda x: x["importance"], reverse=True)
    return normalized_contributions

@app.route("/")
def home():
    return render_template("index.html", model_info=MODEL_INFO)

@app.route("/predict", methods=["POST"])
def predict():
    try:
        ticker = request.json.get("ticker", "").strip().upper()
        if not ticker:
            return jsonify({"error": "Please enter a ticker symbol"}), 400
        data, error = get_latest_data(ticker)
        if error:
            return jsonify({"error": error}), 400
        result = predict_volatility(data)
        feature_contributions = get_feature_contributions(data)
        interpretations = {
            "Low": "The stock is expected to have stable, predictable price movements with minimal risk.",
            "Medium": "The stock may experience moderate price fluctuations. Consider diversification.",
            "High": "The stock is likely to experience significant price swings. High risk, high potential reward."
        }
        response = {
            "success": True,
            "ticker": data["ticker"],
            "date": data["date"],
            "stock_data": {
                "open": data["open"],
                "high": data["high"],
                "low": data["low"],
                "close": data["close"],
                "volume": data["volume"],
                "price_change_pct": data["price_change_pct"]
            },
            "gold_price": data["gold_close"],
            "prediction": result["prediction"],
            "prediction_code": result["prediction_code"],
            "confidence": result["confidence"],
            "probabilities": result["probabilities"],
            "interpretation": interpretations[result["prediction"]],
            "technical_indicators": data["technical_indicators"],
            "historical_volatility": data["historical_volatility"],
            "feature_contributions": feature_contributions,
            "model_info": MODEL_INFO
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
