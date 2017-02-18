#! /usr/bin/env python3
# Create files for users who are home
# Ethan Seyl 2017

from pathlib import Path
from time import sleep
import configparser
import subprocess
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
config = configparser.ConfigParser()
config.read('{}/config/config.ini'.format(dir_path))

users = dict(
    zip((config['DEFAULT']['Users'].split(', ')), (config['HUE']['Devices']
                                                   ).split(', ')))


def ping_devices(users):
    for user in users:
        device = users.get(user)
        print("[ping_devices] {}".format(device))
        output = subprocess.check_output(
            ['sudo', 'hcitool', 'name', device],
            stderr=subprocess.STDOUT).decode('utf-8')
        if output:
            print("[ping_devices] {}'s device is in range.".format(user))
            create_file(user)
        else:
            print("{}'s device unreachable.".format(user))
            delete_file(user)


def does_file_exist(user):
    my_file = Path("{}/users_home/{}_is.home".format(dir_path, user))
    if my_file.is_file():
        print("[does_file_exist] {} file exists.".format(user))
        return True


def create_file(user):
    if not does_file_exist(user):
        open('{}/users_home/{}_is.home'.format(dir_path, user), 'w+b')
        print("[create_file] {} file created.".format(user))


def delete_file(user):
    if does_file_exist(user):
        try:
            os.remove('{}/users_home/{}_is.home'.format(dir_path, user))
            print("[delete_file] {} file deleted.".format(user))
        except Exception as e:
            print("[delete_file] {}".format(str(e)))
    else:
        print("[delete_file] {} file doesn't exist.".format(user))


def main(users):
    while True:
        ping_devices(users)
        sleep(20)


if __name__ == "__main__":
    main(users)
