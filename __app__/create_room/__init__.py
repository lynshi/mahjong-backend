from http import HTTPStatus
import json
import random
import secrets

import azure.functions as func
from loguru import logger

from __app__ import datastore


# pylint: disable=unused-argument
def main(req: func.HttpRequest) -> func.HttpResponse:
    """Get a room code for the "create room" page."""
    logger.info("Creating a new room")

    # For signing JWTs containing player data.
    signing_key = secrets.token_bytes(16).decode("utf-8")

    code_length = 4
    while True:
        room_code = "".join(
            [chr(ord("A") + random.randint(0, 26)) for _ in range(code_length)]
        )
        try:
            datastore.environment.create_room(room_code, signing_key)
        except datastore.environment.RoomCodeExists:
            logger.opt(exception=True).debug("regenerating room code")
            continue

        break

    room_code_response = {"roomCode": room_code}

    return func.HttpResponse(
        json.dumps(room_code_response),
        status_code=HTTPStatus.OK,
        mimetype="application/json",
    )
