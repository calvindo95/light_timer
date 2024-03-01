import time
import datetime
import subprocess
from suntime import Sun
import schedule

hours_on = 6
light_ip_addr = "192.168.1.218"
co2_ip_addr = "192.168.1.212"

def on(ip_addr):
    print(f"{datetime.datetime.now().strftime('%H:%M')}: Turning on {ip_addr}")
    subprocess.run(['/usr/local/bin/hs100', ip_addr, 'on'])

def off(ip_addr):
    print(f"{datetime.datetime.now().strftime('%H:%M')}: Turning off {ip_addr}")
    subprocess.run(['/usr/local/bin/hs100', ip_addr, 'off'])

if __name__=="__main__":
    latitude = 38.51
    longitude = -77.20

    sun = Sun(latitude, longitude)

    curr_time = datetime.datetime.now()

    today_sr = sun.get_local_sunrise_time()
    today_sr_secs = time.mktime(today_sr.timetuple())

    today_ss = sun.get_local_sunset_time()
    today_ss_secs = time.mktime(today_ss.timetuple())

    # calculate co2 on time
    co2_on = today_sr - datetime.timedelta(hours=1)
    schedule.every().day.at(f"{co2_on.strftime('%H:%M')}").do(on, ip_addr=co2_ip_addr)

    # calculate light on time
    light_on = today_sr
    schedule.every().day.at(f"{light_on.strftime('%H:%M')}").do(on, ip_addr=light_ip_addr)

    # calculate co2 off time
    co2_off = today_sr + datetime.timedelta(hours=hours_on - 1)
    schedule.every().day.at(f"{co2_off.strftime('%H:%M')}").do(off, ip_addr=co2_ip_addr)

    # calculate light off time
    light_off = today_sr + datetime.timedelta(hours=hours_on)
    schedule.every().day.at(f"{light_off.strftime('%H:%M')}").do(off, ip_addr=light_ip_addr)

    # print current time
    print(f"Current time: {curr_time.strftime('%m/%d/%y %H:%M')}")
    print(f"CO2 on at {co2_on.strftime('%H:%M')}")
    print(f"Light on at {light_on.strftime('%H:%M')}")
    print(f"CO2 off at {co2_off.strftime('%H:%M')}")
    print(f"SS time and light off at {light_off.strftime('%H:%M')}")

    print(schedule.get_jobs())

    while today_ss_secs > time.mktime(datetime.datetime.now().timetuple()):
        schedule.run_pending()
        time.sleep(1)