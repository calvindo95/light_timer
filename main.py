import time
import datetime
import subprocess
from suntime import Sun
import schedule
import logging
import os

import config

def on(ip_addr):
    print(f"{datetime.datetime.now().strftime('%H:%M')}: Turning on {ip_addr}")
    subprocess.run(['/usr/local/bin/hs100', ip_addr, 'on'])

def off(ip_addr):
    print(f"{datetime.datetime.now().strftime('%H:%M')}: Turning off {ip_addr}")
    subprocess.run(['/usr/local/bin/hs100', ip_addr, 'off'])

def initialize_logging():
    if not os.path.isdir(config.log_dir):
        os.mkdir(config.log_dir)
    logging.basicConfig(filename=config.log_dir+"logging.log", format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', encoding='utf-8', level=logging.INFO)

if __name__=="__main__":
    initialize_logging()

    latitude = 38.51
    longitude = -77.20

    sun = Sun(latitude, longitude)
    today_sr = sun.get_local_sunrise_time()

    # calculate co2 on time
    co2_on = today_sr - datetime.timedelta(hours=1)
    schedule.every().day.at(f"{co2_on.strftime('%H:%M')}").do(on, ip_addr=config.co2_ip_addr)

    # calculate light on time
    light_on = today_sr + datetime.timedelta(hours=1)
    schedule.every().day.at(f"{light_on.strftime('%H:%M')}").do(on, ip_addr=config.light_ip_addr)

    # calculate co2 off time
    co2_off = co2_on + datetime.timedelta(hours=config.hours_on)
    schedule.every().day.at(f"{co2_off.strftime('%H:%M')}").do(off, ip_addr=config.co2_ip_addr)

    # calculate light off time
    light_off = light_on + datetime.timedelta(hours=config.hours_on)
    schedule.every().day.at(f"{light_off.strftime('%H:%M')}").do(off, ip_addr=config.light_ip_addr)

    # print current time
    logging.info(f"CO2 on at {co2_on.strftime('%H:%M')}")
    logging.info(f"Light on at {light_on.strftime('%H:%M')}")
    logging.info(f"CO2 off at {co2_off.strftime('%H:%M')}")
    logging.info(f"Light off at {light_off.strftime('%H:%M')}")
    logging.info(f"Scheduled jobs at: {schedule.get_jobs()}")

    while time.mktime(light_off.timetuple())+10 > time.mktime(datetime.datetime.now().timetuple()):
        schedule.run_pending()
        time.sleep(1)

    logging.warning(f"Done executing schedule")