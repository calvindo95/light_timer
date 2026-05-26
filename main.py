import time
import datetime
from dateutil import tz
import subprocess
from suntime import Sun
import schedule
import logging
import logging.handlers
import os
import signal

import config

running = True

def on(ip_addr):
    logging.info(f"Turning on {ip_addr}")
    proc = subprocess.run(['/usr/local/bin/hs100', ip_addr, 'on'], capture_output=True)
    if proc.stderr.decode():
        logging.info(f"Failed to turn on {ip_addr} with error: {proc.stderr.rstrip().decode()}")

def off(ip_addr):
    logging.info(f"Turning off {ip_addr}")
    proc = subprocess.run(['/usr/local/bin/hs100', ip_addr, 'off'], capture_output=True)
    if proc.stderr.decode():
        logging.info(f"Failed to turn off {ip_addr} with error: {proc.stderr.rstrip().decode()}")

def schedule_daily_jobs():
    schedule.clear('daily')

    sun = Sun(38.51, -77.20)
    today_sr = sun.get_sunrise_time(time_zone=tz.gettz('US/Eastern'))

    co2_on = today_sr
    light_on = today_sr + datetime.timedelta(hours=2)
    co2_off = co2_on + datetime.timedelta(hours=config.hours_on)
    light_off = light_on + datetime.timedelta(hours=config.hours_on)

    schedule.every().day.at(co2_on.strftime('%H:%M')).do(on, ip_addr=config.co2_ip_addr).tag('daily')
    schedule.every().day.at(light_on.strftime('%H:%M')).do(on, ip_addr=config.light_ip_addr).tag('daily')
    schedule.every().day.at(co2_off.strftime('%H:%M')).do(off, ip_addr=config.co2_ip_addr).tag('daily')
    schedule.every().day.at(light_off.strftime('%H:%M')).do(off, ip_addr=config.light_ip_addr).tag('daily')

    logging.info(f"CO2 on at {co2_on.strftime('%H:%M')}")
    logging.info(f"Light on at {light_on.strftime('%H:%M')}")
    logging.info(f"CO2 off at {co2_off.strftime('%H:%M')}")
    logging.info(f"Light off at {light_off.strftime('%H:%M')}")

def initialize_logging():
    if not os.path.isdir(config.log_dir):
        os.mkdir(config.log_dir)
    handler = logging.handlers.RotatingFileHandler(
        config.log_dir + "logging.log",
        maxBytes=1_000_000,
        backupCount=3,
    )
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.INFO)

def handle_signal(signum, _frame):
    global running
    logging.info(f"Received signal {signum}, shutting down")
    running = False

if __name__ == "__main__":
    initialize_logging()

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    logging.info("Light timer service starting")
    schedule_daily_jobs()

    # Recalculate sunrise-based times each day
    schedule.every().day.at("00:01").do(schedule_daily_jobs)

    while running:
        schedule.run_pending()
        time.sleep(1)

    logging.info("Light timer service stopped")
