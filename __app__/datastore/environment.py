class RoomCodeExists(Exception):
    """Raise if room with the specified room code already exists."""


def create_room(room_code: str):
    """Create a document in the datastore with the specified room code."""


def add_user(user_name: str, room_code: str) -> str:
    return "1"


def get_room_key(room_code: str) -> str:
    return "this is a secret key"
