#! /usr/bin/env python3
# Wemo Control
# Ethan Seyl 2017

from pathlib import Path
import logging.config
import configparser
import subprocess
import requests
import os

config = configparser.ConfigParser()
dir_path = os.path.dirname(os.path.realpath(__file__))
config.read('{}/config/config.ini'.format(dir_path))


def check_for_user():
    for user in config['DEFAULT']['Users'].split(', '):
        user_file = Path("{}/users_home/{}_is.home".format(dir_path, user))
        if user_file.is_file():
            return True


def ping_cam():
    output = subprocess.Popen(
        ['ping', '-c', '1', '192.168.1.111'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    output = (output.stdout.read()).decode('utf-8')
    print("[ping_cam] {}".format(output))
    if '100.0% packet loss' in output or 'Unreachable' in output:
        return True
    else:
        return False


def ifttt_trigger(value):
    requests.post('https://maker.ifttt.com/trigger/{}/with/key/{}'.format(
        value, config['WEMO']['IFTTTApiKey']))
    logging.info("[wemo][ifttt_trigger] Recipe '{}' triggered".format(value))
    exit


def main():
    if check_for_user():
        if ping_cam():
            logging.debug("[wemo][main] Already off.")
        else:
            ifttt_trigger('wemo_off')
    else:
        if ping_cam():
            ifttt_trigger('wemo_on')
        else:
            logging.debug("[wemo][main] Already on.")


if __name__ == '__main__':
    logging.config.fileConfig('{}/config/logging.conf'.format(dir_path))
    main()
