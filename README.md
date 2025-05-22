# Swing Trade Auto Bot (Nifty 50 + Midcap 100)

This is a fully automated swing trading system that:
- Scans all Nifty 50 + Midcap 100 stocks daily at 6 PM IST
- Places trades automatically at 9:15 AM IST via Zerodha Kite
- Logs signals and decisions into a connected Google Sheet

---

## 📂 Project Structure

| File                    | Description                                  |
|-------------------------|----------------------------------------------|
| `signal_generator.py`   | Analyzes 150 stocks daily and logs signals to Google Sheet  
| `auto_trade_executor.py`| Places trades via Zerodha Kite API  
| `main.py`               | Schedules both scripts to run on time using `schedule`  
| `stock_universe.py`     | Contains all 150 ticker symbols  
| `requirements.txt`      | Required Python packages for Render  
| `README.md`             | Deployment and usage guide  

---

## 🔧 Required Environment Variables (Set in Render)

| Variable Name          | Description                                |
|------------------------|--------------------------------------------|
| `GOOGLE_CREDS_JSON`    | Single-line version of your credentials.json  
| `KITE_API_KEY`         | From your Zerodha Developer App  
| `KITE_API_SECRET`      | From your Zerodha Developer App  
| `KITE_REQUEST_TOKEN`   | Refresh manually each morning from Kite login  

---

## 🚀 Render Deployment (Background Worker)

### Step 1: Go to https://dashboard.render.com/

- Create a **New Web Service** > Select **Background Worker**
- Choose **Manual Deploy from Zip**
- Upload this project `.zip` file
- Set `Start Command` as:
  ```bash
  python main.py
  ```

### Step 2: Configure Environment Variables

Set the following inside Render → Environment tab:

```env
GOOGLE_CREDS_JSON=your_google_service_account_json_as_single_line
KITE_API_KEY=your_zerodha_api_key
KITE_API_SECRET=your_zerodha_api_secret
KITE_REQUEST_TOKEN=your_daily_request_token (must update every day before 9:15 AM)
```

---

## 🔁 Daily Usage

- Each morning:
  1. Visit: `https://kite.trade/connect/login?api_key=your_api_key`
  2. Log in to Zerodha and copy the `request_token` from the URL
  3. Update the `KITE_REQUEST_TOKEN` value in Render → Environment
  4. No need to redeploy — the bot will use the updated token automatically

---

## ✅ Scheduled Tasks (India Time)

| Time        | Task                        | Script                 |
|-------------|-----------------------------|------------------------|
| 6:00 PM IST | Market scan and signal log  | `signal_generator.py`  
| 9:15 AM IST | Place trades (Buy orders)   | `auto_trade_executor.py`  

---

## 🔐 Security Notes

- Never hardcode your credentials — always use environment variables
- Keep your API secret and access tokens safe
- You may rotate your API keys regularly via Zerodha Developer Portal

---

Happy Trading!
