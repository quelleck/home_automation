#!/usr/bin/env python3
#
# Ethan Seyl

from time import sleep
import subprocess
import glob


def command(on_or_off):
    subprocess.call(["sudo /home/pi/home_automation/hdmi_control/hdmi_control {}".format(on_or_off)], shell=True)


while True:
    if glob.glob('/home/pi/home_automation/users_home/*.home'):
        command('on')
    else:
        command('off')
    sleep(5)

