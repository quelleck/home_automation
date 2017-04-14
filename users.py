#! /usr/bin/env python3
# Create files for users who are home
# Ethan Seyl 2017

from pathlib import Path
from time import sleep
import logging.config
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
        logging.debug("[users][ping_devices] {}".format(device))
        output = get_response(device)
        if output:
            logging.debug(
                "[users]ping_devices] {}'s device is in range.".format(user))
            create_file(user)
        else:
            logging.debug(
                "[users][ping_devices] {}'s device unreachable.".format(user))
            delete_file(user)


def get_response(device):
    tries = 1
    while tries <= 3:
        try:
            output = subprocess.check_output(
                ['sudo', 'hcitool', 'name', device],
                stderr=subprocess.STDOUT).decode('utf-8')
            logging.debug("[users][get_response] Scan result = {}".format(output))
        except Exception as e:
            logging.error("[users][ping_devices] Exception = {}".format(e))
            exit()
        if not output:
            logging.debug("[users][get_response] Attempt {}/3 for device {} failed".format(tries, device))
            tries += 1
            sleep(1)
        else:
            return output
    return output

def does_file_exist(user):
    my_file = Path("{}/users_home/{}_is.home".format(dir_path, user))
    if my_file.is_file():
        logging.debug("[users][does_file_exist] {} file exists.".format(user))
        return True


def create_file(user):
    if not does_file_exist(user):
        open('{}/users_home/{}_is.home'.format(dir_path, user), 'w+b')
        logging.debug("[users][create_file] {} file created.".format(user))


def delete_file(user):
    if does_file_exist(user):
        try:
            os.remove('{}/users_home/{}_is.home'.format(dir_path, user))
            logging.debug("[users][delete_file] {} file deleted.".format(user))
        except Exception as e:
            logging.debug("[users][delete_file] {}".format(str(e)))
    else:
        logging.debug(
            "[users][delete_file] {} file doesn't exist.".format(user))


def main(users):
    while True:
        ping_devices(users)
        sleep(10)


if __name__ == "__main__":
    logging.config.fileConfig('{}/config/users_logging.conf'.format(dir_path))
    main(users)
