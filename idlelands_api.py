import requests
import json
import os
from simplejson.decoder import JSONDecodeError
from idlelands_player import IdleLandsPlayer

API_ROOT = 'http://api.idle.land'
API_ROOT_DIRECT = 'http://192.99.68.70'
HOST = 'api.idle.land'
POST = 'POST'
PUT = 'PUT'
GET = 'GET'
PATCH = 'PATCH'
TIMEOUT = 10


class IdleLandsException(Exception):
    def __init__(self, verb, route, request_data, response):
        super(IdleLandsException, self).__init__()
        self.req_verb = verb
        self.req_route = route
        self.req_data = request_data
        self.response = response

        self.code = int(response['code']) if 'code' in response else -1
        self.message = response['message'] if 'message' in response else None

    def __str__(self):
        return 'IdleLandsException(%s, %r) code %i: %r' % (self.req_verb, self.req_route, self.code, self.message)


class IdleLandsAPI(object):
    session = requests.session()  # for global connection reuse

    def __init__(self, identifier, password=None, token=None, direct=False):
        super(IdleLandsAPI, self).__init__()
        self.identifier = identifier
        self._password = password
        self.token = token
        self.direct = direct

    @staticmethod
    def from_config(config_filepath='auth.conf', direct=False):
        with open(config_filepath, 'r') as f:
            identifier, password = f.readline().strip().split(' ', 1)

        idle = IdleLandsAPI(identifier, password, direct=direct)
        return idle

    @staticmethod
    def api_request(verb, route, request_data, direct=False):
        assert len(route) > 0 and route[0] == '/'

        headers = {
            'Content-Type': 'application/json',
            'Host': HOST
        }

        response = IdleLandsAPI.session.request(verb,
                                                '%s%s' % (API_ROOT if not direct else API_ROOT_DIRECT, route),
                                                data=json.dumps(request_data),
                                                headers=headers,
                                                timeout=TIMEOUT)
        try:
            response = response.json()
        except JSONDecodeError:
            raise IdleLandsException(verb, route, request_data, response)

        if 'isSuccess' not in response or not response['isSuccess']:
            raise IdleLandsException(verb, route, request_data, response)

        return response

    def request(self, verb, route, request_data):
        request_data.update({
            'identifier': self.identifier,
            'token': self.token
        })
        return IdleLandsAPI.api_request(verb, route, request_data, self.direct)

    @staticmethod
    def map(map_name, direct=False):
        try:
            return IdleLandsAPI.api_request(POST, '/game/map', {
                'map': map_name
            }, direct=direct)
        except IdleLandsException, e:  # work around #474
            return e.response

    @staticmethod
    def battle(battle_id, direct=False):
        return IdleLandsAPI.api_request(POST, '/game/battle', {
            'battleId': battle_id
        }, direct=direct)

    def turn(self):
        return IdleLandsPlayer(self.request(POST, '/player/action/turn', {})['player'])

    ###################
    ### Player Auth ###
    ###################

    @staticmethod
    def register(identifier, name, password):
        return IdleLandsAPI.api_request(PUT, '/player/auth/register', {
            'identifier': identifier,
            'name': name,
            'password': password
        })

    def login(self, password=None, identifier=None):
        if password is not None:
            self._password = password
        if identifier is not None:
            self.identifier = identifier

        response = IdleLandsAPI.api_request('POST', '/player/auth/login', {
            'identifier': self.identifier,
            'password': self._password
        })
        self.token = response['player']['tempSecureToken']
        return response

    def logout(self):
        return self.request(POST, '/player/auth/logout', {})

    #########################
    ### Player Management ###
    #########################

    def set_gender(self, gender):
        return self.request(PUT, '/player/manage/gender', {
            'gender': gender,
        })

    def add_to_inventory(self, item_slot):
        return self.request(PUT, '/player/manage/inventory/add', {
            'itemSlot': item_slot,
        })

    def sell_item(self, inv_slot):
        return self.request(POST, '/player/manage/inventory/sell', {
            'invSlot': inv_slot,
        })

    def swap_item(self, inv_slot):
        return self.request(PATCH, '/player/manage/inventory/sell', {
            'invSlot': inv_slot,
        })

    def add_personality(self, new_pers):
        return self.request(PUT, '/player/manage/personality/add', {
            'newPers': new_pers
        })

    def remove_personality(self, old_pers):
        return self.request(POST, '/player/manage/personality/remove', {
            'oldPers': old_pers
        })

    def add_priority(self, stat, points):
        return self.request(PUT, '/player/manage/priority/add', {
            'stat': stat,
            'points': points
        })

    def remove_priority(self, stat, points):
        return self.request(POST, '/player/manage/priority/remove', {
            'stat': stat,
            'points': points
        })

    def set_pushbullet_key(self, api_key):
        return self.request(PUT, '/player/manage/pushbullet/set', {
            'apiKey': api_key
        })

    def remove_pushbullet_key(self, old_pers):
        return self.request(POST, '/player/manage/pushbullet/remove', {})

    def set_string(self, string_type, message):
        return self.request(PUT, '/player/manage/string/add', {
            'type': string_type,
            'msg': message
        })

    def remove_string(self, string_type):
        return self.request(POST, '/player/manage/string/remove', {
            'type': string_type
        })