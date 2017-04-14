#! /usr/bin/env python3
# Ecobee3 Control
# Ethan Seyl 2017

from time import sleep
import logging.config
import configparser
import requests
import datetime
import json
import os

config = configparser.ConfigParser()
dir_path = os.path.dirname(os.path.realpath(__file__))
config.read('{}/config/config.ini'.format(dir_path))

away_json = {
  "selection": {
    "selectionType":"registered",
    "selectionMatch":""
  },
  "functions": [
    {
      "type":"setHold",
      "params":{
        "holdType":"nextTransition",
        "holdClimateRef":"away"
      }
    }
  ]
}

def get_access_token():
    api_key = config['ECOBEE3']['EcobeeApiKey']
    refresh_token = config['ECOBEE3']['EcobeeRefreshToken']
    h = {'Content-Type': 'application/json;charset=UTF-8'}
    url = 'https://api.ecobee.com/token'
    data = 'grant_type=refresh_token&code={}&client_id={}'.format(refresh_token, api_key)
    return post(url, data, h)


def post(url, params, headers):
    try:
        return requests.post(url, params=params, headers=headers)
    except requests.exceptions.ConnectionError as e:
        logging.error("[ecobee3][post] Connection error: {}".format(e))
    except Exception as e:
        print("GENERIC EXCEPTION: {}".format(e))


def auth_expires(response):
    auth = response.json()
    auth_expires = datetime.datetime.now() + datetime.timedelta(minutes=int(auth['expires_in']))
    print("[ecobee3][auth_expires] Auth Expires: {}".format(auth_expires))
    return auth_expires


def set_away(access_token):
    auth = access_token.json()['access_token']
    url = 'https://api.ecobee.com/1/thermostat?format=json'
    data = away_json
    h = {'Content-Type': 'application/json;charset=UTF-8', 'Authorization': 'Bearer {}'.format(auth)}
    return post(url, data, h)
    # curl - s - -request
    # POST - -data - urlencode @ json.txt - H
    # "Content-Type: application/json;charset=UTF-8" - H
    # "Authorization: Bearer udIB8O0i1k7otRox9gTYcHbuTX6oRI4S" "https://api.ecobee.com/1/thermostat?format=json"


def main():
    print("ECOBEE TIME")
    access_token = get_access_token()
    print("Access Token: {}".format(access_token.json()))
    auth_expires(access_token)
    away = set_away(access_token)
    print(away.json())


if __name__ == '__main__':
    logging.config.fileConfig('{}/config/ecobee3_logging.conf'.format(dir_path))
    main()
