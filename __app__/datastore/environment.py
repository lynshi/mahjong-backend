import backoff
from loguru import logger
import pymongo
from pymongo import MongoClient

from __app__ import model

from . import constants
from .config import COSMOS_CONNECTION_STRING


class RoomCodeExists(Exception):
    """Raise if a room with the specified room code already exists."""


class UnknownRoomCode(Exception):
    """Raise if no room with the code is found in the datastore."""


@logger.catch(reraise=True)
@backoff.on_exception(backoff.constant, pymongo.errors.ConnectionFailure, max_tries=3)
@logger.catch(reraise=True, level="WARNING")
def create_room(room_code: str, signing_key: str):
    """Creates a document in the datastore with the specified room code."""

    client = MongoClient(COSMOS_CONNECTION_STRING)
    rooms = client.mahjong.rooms

    try:
        rooms.insert_one(
            {
                constants.room.ID: room_code,
                constants.room.NEXT_PLAYER_ID: 0,
                constants.room.PLAYERS: {},
                constants.room.SIGNING_KEY: signing_key,
            }
        )
    except pymongo.errors.DuplicateKeyError:
        raise RoomCodeExists(room_code)


@logger.catch(reraise=True)
@backoff.on_exception(backoff.constant, pymongo.errors.ConnectionFailure, max_tries=3)
@logger.catch(reraise=True, level="WARNING")
def add_player(player_name: str, room_code: str) -> model.Player:
    """Adds a player to an existing room and returns their player ID."""

    client = MongoClient(COSMOS_CONNECTION_STRING)
    rooms = client.mahjong.rooms

    room = rooms.find_one_and_update(
        {constants.room.ID: room_code},
        {"$inc": {constants.room.NEXT_PLAYER_ID: 1}},
        return_document=pymongo.ReturnDocument.BEFORE,
    )

    if room is None:
        raise UnknownRoomCode(room_code)

    player_id = str(room[constants.room.NEXT_PLAYER_ID])
    signing_key = room[constants.room.SIGNING_KEY]

    rooms.update_one(
        {constants.room.ID: room_code},
        {
            "$set": {
                f"{constants.room.PLAYERS}.{player_id}": {
                    constants.player.ID: player_id,
                    constants.player.NAME: player_name,
                }
            }
        },
    )

    return model.Player(player_id, player_name, room_code, signing_key)


@logger.catch(reraise=True)
@backoff.on_exception(backoff.constant, pymongo.errors.ConnectionFailure, max_tries=3)
@logger.catch(reraise=True, level="WARNING")
def get_room_signing_key(room_code: str) -> str:
    """Retrieve the key used to sign JWTs for a particular room."""
    client = MongoClient(COSMOS_CONNECTION_STRING)
    rooms = client.mahjong.rooms

    room = rooms.find_one(filter={constants.room.ID: room_code,})

    return room[constants.room.SIGNING_KEY]
