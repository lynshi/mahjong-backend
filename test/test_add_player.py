# pylint: disable=missing-function-docstring

import json
from unittest.mock import patch

import azure.functions as func

from __app__.add_player import main
from __app__ import datastore

from . import common


def test_add_player():
    player_id = "0"
    player_name = "Alice"
    signing_key = "signing key"

    room_code = 'ABCD'

    connection_info_json = {
        "url": "https://signalr/?hub=hub",
        "accessToken": "accessToken"
    }

    token = 'token'

    with patch(
        "__app__.create_room.datastore.environment.add_player"
    ) as add_player_mock:
        add_player_mock.return_value = datastore.model.Player(player_id, player_name, signing_key)

        with patch('jwt.encode') as encode_mock:
            encode_mock.return_value = token.encode("utf-8")

            request = func.HttpRequest("POST", "/api/add_player", body=json.dumps({
                'name': player_name,
                'roomCode': room_code,
            }).encode())

            response = main(request, json.dumps(connection_info_json))

    add_player_mock.assert_called_once_with(player_name, room_code)
    encode_mock.assert_called_once_with({
        'playerId': player_id,
    }, signing_key, algorithm='HS256')

    assert common.get_json(response) == {
        **connection_info_json,
        **{
            'playerId': player_id,
            'playerIdToken': token
        }
    }
