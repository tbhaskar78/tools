#!/usr/bin/env python3
'''
 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at https://mozilla.org/MPL/2.0/.


 Author: Bhaskar Tallamraju 
 Date: July 08, 2020
'''
import time
import subprocess
import syslog
from datetime import datetime

'''
 amount of time to check before declaring system idle  (in seconds)
'''
IDLE_TIME_SET=300

# this function could be used to check for network activity and suspend based on it
def get_rxpackets(iface="wlp3s0"):
    with open('/sys/class/net/{}/statistics/rx_packets'.format(iface), 'r') as file:
        rxPkts = file.read().replace('\n', '')
    return int(rxPkts)

# this function could be used to add date and time to logs if needed
def get_currentDateTime():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

'''
 this function gets the inactivity time - this is used in this code to initiate a suspend
 remember, adding this to crontab may not work, as DISPLAY is not exported.
 Recommend using startup instead or export the DISPLAY. However, if you switch monitors
 this may break till the next restart.
'''
def get_idle():
    return int(int(subprocess.check_output("/usr/bin/xprintidle").decode("utf-8").strip())/1000)


if __name__ == "__main__":
    error_check = 0
    count = 0
    while error_check < 5:
        try:
            syslog.syslog("IDLE_CHECK: Starting idle_check\n")
            while True:
                time.sleep(10)
                idletime = get_idle()
                if count > 3600:
                    if idletime < 10:
                        syslog.syslog("IDLE_CHECK: System is active...\n")
                if idletime > 20 and idletime < 30:
                    syslog.syslog("IDLE_CHECK: System inactive for more than 20 secs, will suspend automatically after 5 mins...\n")
                elif idletime > 150 and idletime < 160:
                    syslog.syslog("IDLE_CHECK: System inactive for more than 2.5 mins, will suspend automatically after 5 mins...\n")
                elif idletime > 240 and idletime < 250:
                    syslog.syslog("IDLE_CHECK: System inactive for more than 4 mins, will suspend automatically after 5 mins...\n")

                if (idletime > IDLE_TIME_SET):
                    syslog.syslog("IDLE_CHECK: System inactive for last 5 mins. Suspending it now to save battery. \n")
                    subprocess.Popen(["systemctl", "suspend", "-i"])
        except Exception as e:
            syslog.syslog("IDLE_CHECK: exception caught {}, retrying. Number of exceptions caught ".format(e) + str(error_check))
            error_check += 1
    syslog.syslog("IDLE_CHECK: multiple exceptions caught, exiting !")
    exit(0)
