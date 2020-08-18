# pylint: disable=missing-function-docstring

from unittest.mock import patch

import azure.functions as func

from __app__.create_room import main
from __app__ import datastore

from . import common


def test_create_room():
    with patch(
        "__app__.create_room.datastore.environment.create_room"
    ) as create_room_mock:
        create_room_mock.return_value = None
        request = func.HttpRequest("GET", "/api/create_room", body=None)

        response = main(request)

    response_json = common.get_json(response)

    assert "roomCode" in response_json
    assert len(response_json["roomCode"]) == 4

    create_room_mock.assert_called_once()


def test_create_room_ensures_code_is_unique():
    with patch(
        "__app__.create_room.datastore.environment.create_room"
    ) as create_room_mock:
        create_room_mock.side_effect = [datastore.environment.RoomCodeExists, None]

        request = func.HttpRequest("GET", "/api/create_room", body=None)

        response = main(request)

    response_json = common.get_json(response)

    assert "roomCode" in response_json
    assert len(response_json["roomCode"]) == 4

    assert create_room_mock.call_count == 2
