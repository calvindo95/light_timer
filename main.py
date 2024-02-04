import time
import datetime
import subprocess
from suntime import Sun

hours_on = 5
ip_addr = "192.168.1.218"

def on():
    print("On")
    subprocess.Popen(['hs100', ip_addr, 'on'])

def off():
    print("Off")
    subprocess.Popen(['hs100', ip_addr, 'off'])

if __name__=="__main__":
    latitude = 38.51
    longitude = -77.20

    sun = Sun(latitude, longitude)

    curr_time = datetime.datetime.now()
    curr_time_secs = time.mktime(curr_time.timetuple())

    today_ss = sun.get_local_sunset_time()
    today_ss_secs = time.mktime(today_ss.timetuple())

    light_on = today_ss - datetime.timedelta(hours=hours_on)
    light_on_secs = time.mktime(light_on.timetuple())

    # print current time
    print(f"current time: {curr_time.strftime('%H:%M')}")
    print(f"current time in seconds: {curr_time_secs}")

    # print sunset time    
    print(f"ss: {today_ss.strftime('%H:%M')}")
    print(f"ss in seconds: {today_ss_secs}")

    # print light on time
    print(f"Light on at: {light_on.strftime('%H:%M')}")
    print(f"Light on at in seconds: {light_on_secs}")


    # calculate sleep until light on
    
    sleep_timer = None

    # if curr_time is past light_on, sleep until today_ss
    if today_ss_secs > curr_time_secs > light_on_secs:
        # sleep until light off
        sleep_timer = today_ss_secs - curr_time_secs
        print(f"Sleeping until sunset: {sleep_timer}")
        time.sleep(sleep_timer)

        off()

    # if curr_time is before light_on, sleep until light_on
    elif today_ss_secs > light_on_secs > curr_time_secs:
        # sleep until light_on
        sleep_timer = light_on_secs - today_ss_secs
        print(f"Sleeping until light on: {sleep_timer}")
        time.sleep(sleep_timer)

        on()

        # sleep until sunset
        sleep_timer = today_ss_secs - light_on_secs
        print(f"Sleeping until sunset: {sleep_timer}")
        time.sleep(sleep_timer)

        off()
    else:
        print("Timer is past sunset; Doing nothing")