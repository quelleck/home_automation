#! /usr/bin/env python3
# Create files for users who are home
# Ethan Seyl 2017

from pathlib import Path
from time import sleep
import logging.config
import configparser
import subprocess
import base64
import paramiko
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
config = configparser.ConfigParser()
config.read('{}/config/config.ini'.format(dir_path))

remote = True
client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

users = dict(
    zip((config['DEFAULT']['Users'].split(', ')), (config['HUE']['Devices']
                                                   ).split(', ')))

remote = config['DEFAULT']['Remote']


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
    if remote:
        users_home = []
        client.connect(config['DEFAULT']['RemoteServer'], username=config['DEFAULT']['RemoteUser'], password=config['DEFAULT']['RemotePw'])
        stdin, stdout, stderr = client.exec_command('ls ~/home_automation/users_home/')
        for line in stdout:
            users_home.append(line.strip('\n'))
        client.close()
        print(users_home)
        print(user)
        if "{}_is.home".format(user) in users_home:
            logging.debug("[users][does_file_exist] {} file exists remotely.".format(user))
            return True
    else:
        my_file = Path("{}/users_home/{}_is.home".format(dir_path, user))
        if my_file.is_file():
            logging.debug("[users][does_file_exist] {} file exists.".format(user))
            return True


def create_file(user):
    if not does_file_exist(user):
        if remote:
            client.connect(config['DEFAULT']['RemoteServer'], username=config['DEFAULT']['RemoteUser'], password=config['DEFAULT']['RemotePw'])
            client.exec_command('touch ~/home_automation/users_home/{}_is.home'.format(user))
            logging.debug("[users][create_file] {} file created remotely.".format(user))
        else:
            open('{}/users_home/{}_is.home'.format(dir_path, user), 'w+b')
            logging.debug("[users][create_file] {} file created.".format(user))


def delete_file(user):
    if does_file_exist(user):
        if remote:
            try:
                client.connect(config['DEFAULT']['RemoteServer'], username=config['DEFAULT']['RemoteUser'], password=config['DEFAULT']['RemotePw'])
                client.exec_command('rm ~/home_automation/users_home/{}_is.home'.format(user))
                logging.debug("[users][create_file] {} file created remotely.".format(user))
            except Exception as e:
                logging.debug("[users][delete_file] Remote: {}".format(str(e)))
        else:
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
