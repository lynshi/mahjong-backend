# pylint: disable=missing-function-docstring

import pymongo
import pytest
from testcontainers.mongodb import MongoDbContainer

from __app__ import model
from __app__.datastore import constants, environment


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

    signing_key = "signing_key"
    environment.create_room(room_code, signing_key)

    room = client.mahjong.rooms.find_one({constants.room.ID: room_code})
    assert room is not None

    expected_room = {
        constants.room.ID: room_code,
        constants.room.PLAYERS: {},
        constants.room.NEXT_PLAYER_ID: 0,
        constants.room.SIGNING_KEY: signing_key,
    }

    assert room == expected_room


# pylint: disable=unused-argument
def test_create_room_catches_duplicate_key(client: pymongo.MongoClient):
    room_code = next(unique_id)

    signing_key = "signing_key"
    environment.create_room(room_code, signing_key)

    with pytest.raises(environment.RoomCodeExists) as exec_info:
        environment.create_room(room_code, signing_key)

    assert str(exec_info.value) == str(environment.RoomCodeExists(room_code))


def test_add_player(client: pymongo.MongoClient):
    room_code = next(unique_id)

    signing_key = "signing_key"
    environment.create_room(room_code, signing_key)

    alice_id = "0"
    alice_name = "Alice"

    bob_id = "1"
    bob_name = "Bob"

    assert environment.add_player(alice_name, room_code) == model.Player(
        alice_id, alice_name, room_code, signing_key
    )
    assert environment.add_player(bob_name, room_code) == model.Player(
        bob_id, bob_name, room_code, signing_key
    )

    assert client.mahjong.rooms.find_one({"_id": room_code})["players"] == {
        str(alice_id): {
            constants.player.ID: alice_id,
            constants.player.NAME: alice_name,
        },
        str(bob_id): {constants.player.ID: bob_id, constants.player.NAME: bob_name,},
    }


def test_add_player_raises_UnknownRoomCode(client: pymongo.MongoClient):
    room_code = next(unique_id)

    alice_name = "Alice"

    with pytest.raises(environment.UnknownRoomCode):
        environment.add_player(alice_name, room_code)


def test_get_room_signing_key(client: pymongo.MongoClient):
    room_code = next(unique_id)

    signing_key = "top secret!!!"
    environment.create_room(room_code, signing_key)

    assert environment.get_room_signing_key(room_code) == signing_key
