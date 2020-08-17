# pylint: disable=missing-function-docstring
from __app__.datastore.constants.room import NEXT_PLAYER_ID, PLAYERS
from unittest.mock import MagicMock, patch

import pymongo
import pytest
from testcontainers.mongodb import MongoDbContainer

from __app__.datastore import constants, environment, model


@pytest.fixture(scope='session', name='client')
def fixture_client():
    with MongoDbContainer(image="mongo:3.6") as mongo:
        environment.COSMOS_CONNECTION_STRING = mongo.get_connection_url()
        yield mongo.get_connection_client()


def test_create_room(client: pymongo.MongoClient):
    room_code = 'ABCD'
    environment.create_room(room_code)

    room = client.mahjong.rooms.find_one({constants.room.ID: room_code})
    assert room is not None

    document = {
        constants.room.ID: room_code,
        constants.room.PLAYERS: {},
        constants.room.NEXT_PLAYER_ID: 0
    }

    for field, item in document.items():
        assert item == room[field]


# pylint: disable=unused-argument
def test_create_room_catches_duplicate_key(client: pymongo.MongoClient):
    room_code = 'this is not a duplicate'
    environment.create_room(room_code)

    with pytest.raises(environment.RoomCodeExists) as exec_info:
        environment.create_room(room_code)

    assert str(exec_info.value) == str(environment.RoomCodeExists(room_code))


# def test_add_player():
#     room_code = 'ABCD'
#     next_player_id = 1
#     player_name = 'Bob'
#     player_key = 'a' * 16
#     with patch('__app__.datastore.environment.MongoClient') as init_mock:
#         client_mock = MagicMock()
#         init_mock.return_value = client_mock

#         client_mock.mahjong.rooms.find_one_and_update.return_value = {
#             datastore.constants.room.NEXT_PLAYER_ID: next_player_id
#         }

#         with patch('secrets.token_bytes') as token_mock:
#             token_mock.return_value = player_key.encode('utf-8')

#             assert environment.add_player(player_name, room_code) == model.Player(next_player_id, player_key, player_name)

#     client_mock.mahjong.rooms.find_one_and_update.assert_called_once_with(
#         {'_id': room_code},
#         {'$inc': }
#     )
