# Stock Volatility Predictor - Web Application

## Quick Start Guide

### 1. Install Flask
```bash
pip install flask
```

### 2. Run the Application
```bash
python app.py
```

### 3. Access the Web Interface
Open your browser and go to: **http://localhost:5000**

## How to Use

1. Enter a stock ticker symbol (e.g., AAPL, MSFT, TSLA)
2. Click "Predict" or press Enter
3. View the volatility prediction (Low, Medium, or High)
4. Check the confidence levels for each category

## Features

- Real-time stock data fetching using Yahoo Finance
- ML-powered volatility prediction
- Beautiful, responsive UI
- Probability confidence levels
- One-click example tickers

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **ML Model**: Random Forest Classifier
- **Data Source**: yfinance API

## Notes

- The model uses the latest 90 days of stock data
- Gold prices (GC=F) are included as a feature
- Predictions are based on: Open, High, Low, Close, Volume, and Gold Price
