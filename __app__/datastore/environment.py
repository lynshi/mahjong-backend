import pymongo
from pymongo import MongoClient

from . import COSMOS_CONNECTION_STRING
from . import document


class RoomCodeExists(Exception):
    """Raise if room with the specified room code already exists."""


def create_room(room_code: str):
    """Create a document in the datastore with the specified room code."""

    client = MongoClient(COSMOS_CONNECTION_STRING)
    rooms = client.mahjong.rooms

    try:
        rooms.insert_one(document.Room.validate_fields({
            '_id': room_code,
        }))
    except pymongo.errors.DuplicateKeyError:
        raise RoomCodeExists()


def add_user(user_name: str, room_code: str) -> str:
    return "1"


def get_room_key(room_code: str) -> str:
    return "this is a secret key"
