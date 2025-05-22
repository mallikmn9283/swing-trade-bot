import gspread
from oauth2client.service_account import ServiceAccountCredentials
from kiteconnect import KiteConnect
import os
import json
import time

# Google Sheets Setup
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds_dict = json.loads(os.environ['GOOGLE_CREDS_JSON'])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open('SwingTradeSignals').sheet1

# Zerodha Kite Connect Setup
kite = KiteConnect(api_key=os.environ['KITE_API_KEY'])
request_token = os.environ['KITE_REQUEST_TOKEN']
api_secret = os.environ['KITE_API_SECRET']

# Generate session and set access token
data = kite.generate_session(request_token, api_secret=api_secret)
kite.set_access_token(data["access_token"])

# Read open trades from Google Sheet
rows = sheet.get_all_records()
today_trades = [row for row in rows if row['Status'] == 'Open']

for trade in today_trades:
    symbol = trade['Stock Name'] + ".NS"
    qty = 1  # You can change this logic to calculate based on capital

    order_params = {
        "tradingsymbol": symbol,
        "exchange": "NSE",
        "transaction_type": kite.TRANSACTION_TYPE_BUY,
        "quantity": qty,
        "order_type": kite.ORDER_TYPE_MARKET,
        "product": kite.PRODUCT_MIS
    }

    try:
        order_id = kite.place_order(variety=kite.VARIETY_REGULAR, **order_params)
        print(f"✅ Order placed for {symbol}, order ID: {order_id}")
        time.sleep(1)  # Small delay between orders
    except Exception as e:
        print(f"❌ Failed to place order for {symbol}: {e}")
