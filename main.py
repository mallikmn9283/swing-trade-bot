import schedule
import time
import subprocess

def run_market_scan():
    print("Running signal generator at 6 PM...")
    subprocess.call(["python", "signal_generator.py"])

def run_trade_execution():
    print("Running trade executor at 9:15 AM...")
    subprocess.call(["python", "auto_trade_executor.py"])

# Schedule the tasks
schedule.every().day.at("18:00").do(run_market_scan)       # 6:00 PM IST
schedule.every().day.at("09:15").do(run_trade_execution)   # 9:15 AM IST

# Loop forever to run the schedule
while True:
    schedule.run_pending()
    time.sleep(60)
