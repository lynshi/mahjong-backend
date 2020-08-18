# pylint: disable=missing-function-docstring

from http import HTTPStatus
import json
from unittest.mock import patch

import azure.functions as func

from __app__.add_player import main
from __app__ import datastore, utils

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

    json_request = {
        'name': player_name,
        'roomCode': room_code,
    }

    with patch('__app__.utils.request.get_json') as get_json_mock:
        get_json_mock.return_value = json_request

        with patch(
            "__app__.create_room.datastore.environment.add_player"
        ) as add_player_mock:
            add_player_mock.return_value = datastore.model.Player(player_id, player_name, signing_key)

            with patch('jwt.encode') as encode_mock:
                encode_mock.return_value = token.encode("utf-8")

                request = func.HttpRequest("POST", "/api/add_player", body=json.dumps(json_request).encode())

                response = main(request, json.dumps(connection_info_json))

    get_json_mock.assert_called_once_with(request, ('name', 'roomCode',))
    add_player_mock.assert_called_once_with(player_name, room_code)
    encode_mock.assert_called_once_with({
        'playerId': player_id,
    }, signing_key, algorithm='HS256')


    common.validate_response_fields(response)
    assert common.get_json(response) == {
        **connection_info_json,
        **{
            'playerId': player_id,
            'playerIdToken': token
        }
    }


def test_add_player_catches_GetJsonError():
    player_id = "0"
    player_name = "Alice"
    signing_key = "signing key"

    room_code = 'ABCD'

    connection_info_json = {
        "url": "https://signalr/?hub=hub",
        "accessToken": "accessToken"
    }

    token = 'token'

    json_request = {
        'name': player_name,
        'roomCode': room_code,
    }

    with patch('__app__.utils.request.get_json') as get_json_mock:
        get_json_mock.side_effect = utils.request.GetJsonError

        with patch(
            "__app__.create_room.datastore.environment.add_player"
        ) as add_player_mock:
            add_player_mock.return_value = datastore.model.Player(player_id, player_name, signing_key)

            with patch('jwt.encode') as encode_mock:
                encode_mock.return_value = token.encode("utf-8")

                request = func.HttpRequest("POST", "/api/add_player", body=json.dumps(json_request).encode())

                response = main(request, json.dumps(connection_info_json))

    get_json_mock.assert_called_once_with(request, ('name', 'roomCode',))

    common.validate_response_fields(response, status_code=HTTPStatus.BAD_REQUEST, mimetype='text/plain')
    assert response.get_body().decode() == 'JSON error'
