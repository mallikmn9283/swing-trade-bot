# signal_generator.py

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from ta.trend import EMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import AverageTrueRange
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os, json
from stock_universe import stock_list

# Constants
TODAY = datetime.now().date()
START_DATE = TODAY - timedelta(days=30)
CONFIDENCE_THRESHOLD = 8  # Minimum number of indicators to qualify

# Google Sheets Setup
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds_dict = json.loads(os.environ['GOOGLE_CREDS_JSON'])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open('SwingTradeSignals').sheet1

# Scoring to confidence level
def get_confidence_level(score_percent):
    if score_percent < 53:
        return "Red"
    elif 53 <= score_percent <= 65:
        return "Orange"
    elif 66 <= score_percent <= 80:
        return "Yellow"
    else:
        return "Green"

# Core analyzer
def analyze_stock(ticker):
    try:
        df = yf.download(ticker, start=START_DATE.strftime('%Y-%m-%d'), end=TODAY.strftime('%Y-%m-%d'), progress=False)
        if df.shape[0] < 21:
            return None

        df['EMA_9'] = EMAIndicator(df['Close'], window=9).ema_indicator()
        df['EMA_21'] = EMAIndicator(df['Close'], window=21).ema_indicator()
        df['MACD'] = MACD(df['Close']).macd_diff()
        df['RSI'] = RSIIndicator(df['Close']).rsi()
        df['ADX'] = ADXIndicator(df['High'], df['Low'], df['Close']).adx()
        df['ATR'] = AverageTrueRange(df['High'], df['Low'], df['Close']).average_true_range()
        df['STOCH_K'] = StochasticOscillator(df['High'], df['Low'], df['Close']).stoch()
        df['STOCH_D'] = StochasticOscillator(df['High'], df['Low'], df['Close']).stoch_signal()

        last = df.iloc[-1]

        # 15 Indicators
        signals = {
            "EMA_Cross": last['EMA_9'] > last['EMA_21'],
            "MACD_Positive": last['MACD'] > 0,
            "RSI_Strong": last['RSI'] > 60,
            "ADX_Trend": last['ADX'] > 20,
            "STOCH_Bullish": last['STOCH_K'] > last['STOCH_D'],
            "Close_Above_Prev_High": last['Close'] > df['High'].iloc[-2],
            "Volume_Surge": last['Volume'] > df['Volume'].rolling(10).mean().iloc[-1] * 1.5,
            "Price_Above_ATR": last['Close'] > df['Close'].mean() + last['ATR'],
            "Price_Above_21EMA": last['Close'] > last['EMA_21'],
            "RSI_Increasing": df['RSI'].iloc[-1] > df['RSI'].iloc[-5],
            "MACD_Increasing": df['MACD'].iloc[-1] > df['MACD'].iloc[-3],
            "ADX_Increasing": df['ADX'].iloc[-1] > df['ADX'].iloc[-3],
            "Stoch_K_Above_50": last['STOCH_K'] > 50,
            "Close_Above_MA": last['Close'] > df['Close'].rolling(20).mean().iloc[-1],
            "Low_GT_EMA_9": last['Low'] > last['EMA_9']
        }

        passed = [k for k, v in signals.items() if v]
        score = len(passed)

        if score >= CONFIDENCE_THRESHOLD:
            entry = round(last['Close'], 2)
            sl = round(entry - 1.5 * last['ATR'], 2)
            target = round(entry + 2 * (entry - sl), 2)
            confidence_pct = round((score / 15) * 100, 2)

            return [
                TODAY.strftime('%Y-%m-%d'),
                ticker.replace(".NS", ""),
                entry,
                sl,
                target,
                sl,
                confidence_pct,
                get_confidence_level(confidence_pct),
                ", ".join(passed),
                "Open"
            ]
    except Exception as e:
        print(f"Error processing {ticker}: {e}")
        return None

# Collect signals
results = []
for stock in stock_list:
    result = analyze_stock(stock)
    if result:
        results.append(result)

# Write to Google Sheet
if results:
    headers = [
        "Date", "Stock Name", "Entry Price", "Original Stop-Loss", "Target Price",
        "Trailing SL", "Confidence Score (%)", "Confidence Level", "Indicators Triggered", "Status"
    ]
    sheet.clear()
    sheet.append_row(headers)
    for row in results:
        sheet.append_row(row)
else:
    print("No signals passed the filter today.")
