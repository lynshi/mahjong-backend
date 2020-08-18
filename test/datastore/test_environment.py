# pylint: disable=missing-function-docstring

from unittest.mock import call, patch

import pymongo
import pytest
from testcontainers.mongodb import MongoDbContainer

from __app__.datastore import constants, environment, model


@pytest.fixture(scope="session", name="client")
def fixture_client():
    with MongoDbContainer(image="mongo:3.6") as mongo:
        environment.COSMOS_CONNECTION_STRING = mongo.get_connection_url()
        yield mongo.get_connection_client()


def get_unique_id():
    num = 0
    while True:
        yield str(num)
        num += 1


unique_id = get_unique_id()


def test_create_room(client: pymongo.MongoClient):
    room_code = next(unique_id)
    environment.create_room(room_code)

    room = client.mahjong.rooms.find_one({constants.room.ID: room_code})
    assert room is not None

    expected_room = {
        constants.room.ID: room_code,
        constants.room.PLAYERS: {},
        constants.room.NEXT_PLAYER_ID: 0,
    }

    assert room == expected_room


# pylint: disable=unused-argument
def test_create_room_catches_duplicate_key(client: pymongo.MongoClient):
    room_code = next(unique_id)
    environment.create_room(room_code)

    with pytest.raises(environment.RoomCodeExists) as exec_info:
        environment.create_room(room_code)

    assert str(exec_info.value) == str(environment.RoomCodeExists(room_code))


def test_add_player(client: pymongo.MongoClient):
    room_code = next(unique_id)
    environment.create_room(room_code)

    alice_id = "0"
    alice_name = "Alice"
    alice_key = "Alice's key"

    bob_id = "1"
    bob_name = "Bob"
    bob_key = "Bob's key"

    with patch("secrets.token_bytes") as token_mock:
        token_mock.side_effect = [
            alice_key.encode("utf-8"),
            bob_key.encode("utf-8"),
        ]

        assert environment.add_player(alice_name, room_code) == model.Player(
            alice_id, alice_name, alice_key
        )
        assert environment.add_player(bob_name, room_code) == model.Player(
            bob_id, bob_name, bob_key
        )

    token_mock.assert_has_calls([call(16)] * 2)

    assert client.mahjong.rooms.find_one({"_id": room_code})["players"] == {
        str(alice_id): {
            constants.player.NAME: alice_name,
            constants.player.SIGNING_KEY: alice_key,
        },
        str(bob_id): {
            constants.player.NAME: bob_name,
            constants.player.SIGNING_KEY: bob_key,
        },
    }
