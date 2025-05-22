import schedule
import subprocess
import time
from datetime import datetime, timedelta

# Convert IST to UTC (Render uses UTC)
def ist_to_utc(hour, minute=0):
    utc_offset = timedelta(hours=5, minutes=30)
    now_ist = datetime.now()
    run_time_ist = now_ist.replace(hour=hour, minute=minute, second=0, microsecond=0)
    run_time_utc = run_time_ist - utc_offset
    return run_time_utc.hour, run_time_utc.minute

# Wrapper to run any script
def run_script(script_name):
    print(f"[{datetime.now()}] Running: {script_name}")
    subprocess.run(["python", script_name])

# Schedule 6:00 PM IST → signal_generator.py
h1, m1 = ist_to_utc(18, 0)
schedule.every().day.at(f"{h1:02d}:{m1:02d}").do(run_script, script_name="signal_generator.py")

# Schedule 9:15 AM IST → auto_trade_executor.py
h2, m2 = ist_to_utc(9, 15)
schedule.every().day.at(f"{h2:02d}:{m2:02d}").do(run_script, script_name="auto_trade_executor.py")

print("✅ Scheduler started. Waiting for trigger times...")

while True:
    schedule.run_pending()
    time.sleep(30)
