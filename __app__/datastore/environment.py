import secrets

import pymongo
from pymongo import MongoClient

from . import COSMOS_CONNECTION_STRING
from . import constants
from . import model


class RoomCodeExists(Exception):
    """Raise if a room with the specified room code already exists."""


class UnknownRoomCode(Exception):
    """Raise if no room with the code is found in the datastore."""


def create_room(room_code: str):
    """Create a document in the datastore with the specified room code."""

    client = MongoClient(COSMOS_CONNECTION_STRING)
    rooms = client.mahjong.rooms

    try:
        rooms.insert_one({
            constants.room.ID: room_code,
            constants.room.PLAYERS: {},
            constants.room.NEXT_PLAYER_ID: 0,
        })
    except pymongo.errors.DuplicateKeyError:
        raise RoomCodeExists(room_code)


def add_player(player_name: str, room_code: str) -> model.Player:
    """Adds a player to an existing room and returns their player ID."""

    client = MongoClient(COSMOS_CONNECTION_STRING)
    rooms = client.mahjong.rooms

    room = rooms.find_one_and_update({"_id": room_code}, {
        '$inc': {
            constants.room.NEXT_PLAYER_ID
        }
    }, return_document=pymongo.ReturnDocument.BEFORE)

    if room is None:
        raise UnknownRoomCode(room_code)

    player_id = room[constants.room.NEXT_PLAYER_ID]
    player_key = secrets.token_bytes(16).decode('utf-8')
    rooms.update_one({'_id': room_code}, {
        '$set': {
            f'{constants.room.PLAYERS}.{player_id}': {
                constants.player.NAME: player_name,
                constants.player.KEY: player_key
            }
        }
    })

    return model.Player(player_id, player_key, player_name)


def get_room_key(room_code: str) -> str:
    return "this is a secret key"
