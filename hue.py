#! /usr/bin/env python3
# Hue Lights Control
# Ethan Seyl 2017

from pathlib import Path
from time import sleep
import logging.config
import configparser
import requests
import json
import os
import re

dir_path = os.path.dirname(os.path.realpath(__file__))
config = configparser.ConfigParser()
config.read('{}/config/config.ini'.format(dir_path))
bridge_ip = requests.get('https://www.meethue.com/api/nupnp').json()[0][
    'internalipaddress']
data = requests.get('http://{}/api/{}/groups/'.format(bridge_ip, config[
    'HUE']['HueApiKey'])).json()
users = config['DEFAULT']['Users'].split(', ')
rooms_list = config['HUE']['Rooms'].split(' | ')
room_and_group_numbers = list(data.keys())

room_names_list = []

for room in rooms_list:
    room = room.split(', ')
    room_names_list.append(room)

room_numbers = []

for number in room_and_group_numbers:
    for users_rooms in room_names_list:
        for room in users_rooms:
            if data[number]['name'] == room:
                print(data[number]['name'])
                print(room)
                room_numbers.append(number)
                print("ADDED ROOM {}".format(room))
            else:
                print(data[number]['name'])
                print(room)
                print("[hue][room_numbers_not_light_groups] Group number not room: {} {}".format(number, room))
room_numbers = set(room_numbers)

print("ROOM NUMBERS {}".format(room_numbers))


def number_for_user(user):
    user_num = users.index(user)
    return user_num


def check_for_user(user):
    user_file = Path("{}/users_home/{}_is.home".format(dir_path, user))
    if user_file.is_file():
        return True


def lights_in_room(room_name):
    match = r"'" + room_name + "', 'lights': \[([^]]*)"
    lights = re.search(match, data).group(1)
    light_list = list(lights.replace("'", "").split(', '))
    return light_list


def room_names_for_user(user_number):
    room_names_for_user = room_names_list[user_number]
    return room_names_for_user


def room_name_to_number(room_name):
    for room_number in room_numbers:
        if data[room_number]['name'] == room_name:
            return room_number


def room_numbers_for_user(user_number):
    room_names = room_names_for_user(user_number)
    room_numbers = []
    logging.debug("[room_numbers_for_user] ROOMS FOR USER {}: {}".format(user_number,
                                                                 room_names))
    for room_name in room_names:
        room_number = room_name_to_number(room_name)
        room_numbers.append(room_number)
    logging.debug("[room_numbers_for_user] USER {} ROOM NUMBERS: {}".format(
        user_number, room_numbers))
    return room_numbers


def turn_on_rooms_for_user(user):
    rooms = room_numbers_for_user(user)
    index = 0
    for room in rooms:
        turn_on_room(room)
        logging.debug("[turn_on_rooms_for_user] User: {}".format(user))
        logging.debug("[turn_on_rooms_for_user] {} ON".format(room_names_list[user][
            index]))
        index += 1


def are_any_lights_on_in_room(room_number):
    data = groups_get_request(room_number)
    room_on = data['state']['any_on']
    if room_on:
        return True


def turn_on_room(room):
    ct_bri = {'on': True, 'bri': 254, 'ct': 231}
    requests.put(
        'http://{}/api/{}/groups/{}/action'.format(
            bridge_ip, config['HUE']['HueApiKey'], room),
        data=json.dumps(ct_bri))
    logging.debug("[turn_on_room] Room {} on.".format(room))
    sleep(1)


def turn_off_room(room_number):
    payload = {'on': False}
    groups_put_request(payload, room_number)
    logging.debug("[turn_off_room] Room {} off.".format(room_number))


def groups_put_request(payload, room_number):
    try:
        requests.put(
            'http://{}/api/{}/groups/{}/action'.format(
                bridge_ip, config['HUE']['HueApiKey'], room_number),
            data=json.dumps(payload))
        sleep(1)
    except Exception as e:
        logging.debug("[groups_put_request] {}".format(e))


def groups_get_request(room_number):
    r = requests.get('http://{}/api/{}/groups/{}'.format(bridge_ip, config[
        'HUE']['HueApiKey'], room_number))
    sleep(1)
    return r.json()


def blink_ready():
    for room in room_numbers:
        logging.debug("BLINK ROOM: {}".format(room))
        groups_put_request({'alert': 'select'}, room)
        groups_put_request({'alert': 'none'}, room)
    logging.info("[hue][blink_ready] Lights are ready")


def turn_off_or_on(room_numbers, off_on):
    for room_number in room_numbers:
        on = are_any_lights_on_in_room(room_number)
        if on and off_on == 'off':
            turn_off_room(room_number)
        if not on and off_on == 'on':
            turn_on_room(room_number)
        elif not on and off_on == 'off':
            logging.debug("[main] Room {} - Lights are already {}.".format(room_number,
                                                                   off_on))
        elif on and off_on == 'on':
            logging.debug("[main] Room {} - Lights are already {}.".format(room_number,
                                                                   off_on))


def set_all_users_home(users):
    users_home = []
    for user in users:
        users_home.append(users.index(user))
    logging.debug("[hue][set_all_users_home] USERS HOME: {}".format(users_home))
    return users_home


def main():
    logging.debug("[hue][main] Users = {}".format(users))
    logging.debug("[hue][main] Rooms = {}".format(room_names_list))
    blink_ready()
    rooms_on = []
    rooms_off = []
    users_home = set_all_users_home(users)
    turn_off_or_on(room_numbers, 'on')
    while True:
        rooms_to_turn_on = []
        for user_name in users:
            user_num = number_for_user(user_name)
            if check_for_user(user_name):
                if user_num not in users_home:
                    users_home.append(user_num)
                    rooms_to_turn_on.extend(room_numbers_for_user(user_num))
                    logging.debug("[hue][main] {} has come home.".format(user_name))
                else:
                    logging.debug("[hue][main] {} was already home.".format(user_name))
            else:
                if user_num in users_home:
                    users_home.remove(user_num)
                    logging.debug("[hue][main] {} has left.".format(user_name))
                else:
                    logging.debug("[hue][main] {} was already gone.".format(user_name))
        logging.debug("[hue][main] USERS HOME: {}".format(users_home))

        rooms_to_remain_on = []
        for user_num in users_home:
            rooms_to_remain_on.extend(room_numbers_for_user(user_num))
        rooms_to_remain_on = set(rooms_to_remain_on)
        logging.debug("[hue][main] Rooms to remain on: {}".format(rooms_to_remain_on))

        rooms_to_turn_off = [
            room for room in room_numbers if room not in rooms_to_remain_on
        ]
        rooms_to_turn_on = set(rooms_to_turn_on)

        logging.debug("[hue][main] Rooms to turn on {}".format(rooms_to_turn_on))

        if rooms_to_turn_on:
            logging.debug("[hue][main] ROOMS ALREADY ON: {}".format(rooms_on))
            rooms_to_turn_on = [
                room for room in rooms_to_turn_on if room not in rooms_on
            ]
            logging.debug("[hue][main] ADJUSTED RTTO: {}".format(rooms_to_turn_on))
            if rooms_to_turn_on:
                turn_off_or_on(rooms_to_turn_on, 'on')
                rooms_on = rooms_on + rooms_to_turn_on
                logging.debug('[hue][main] ROOMS TURNED ON: {}'.format(rooms_to_turn_on))
                rooms_off = [room for room in rooms_to_turn_off if room not in rooms_on]
        else:
            logging.debug("[hue][main] No rooms to turn on")

        logging.debug("[hue][main] Rooms to turn off {}".format(rooms_to_turn_off))

        if rooms_to_turn_off:
            logging.debug("[hue][main] ROOMS ALREADY OFF: {}".format(rooms_off))
            rooms_to_turn_off = [
                room for room in rooms_to_turn_off if room not in rooms_off
            ]
            logging.debug("[hue][main] ADJUSTED RTTOFF: {}".format(rooms_to_turn_off))
            if rooms_to_turn_off:
                turn_off_or_on(rooms_to_turn_off, 'off')
                rooms_on = [room for room in rooms_to_turn_on]
                rooms_off = [room for room in rooms_to_turn_off if room not in rooms_on]
        else:
            logging.debug("[hue][main] No rooms to turn off")
        logging.debug("[hue][main] Sleep...")
        sleep(5)


if __name__ == "__main__":
    logging.config.fileConfig('{}/config/hue_logging.conf'.format(dir_path))
    main()
