from http import HTTPStatus
import json

import azure.functions as func
import jwt
from loguru import logger

from __app__ import datastore
from __app__ import utils


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Add a player to a room."""
    logger.info("Adding a new player")

    try:
        json_body = utils.request.get_json(req, ("name", "roomCode"))
    except utils.request.GetJsonError:
        logger.opt(exception=True).error("Error getting JSON")
        return func.HttpResponse("JSON error", status_code=HTTPStatus.BAD_REQUEST,)

    player_name = json_body["name"]
    room_code = json_body["roomCode"]

    try:
        player = datastore.environment.add_player(player_name, room_code)
    except datastore.environment.UnknownRoomCode:
        logger.opt(exception=True).error("Room code does not exist")
        return func.HttpResponse(
            "Invalid room code", status_code=HTTPStatus.BAD_REQUEST,
        )

    response_json = player.to_dict_with_jwt()

    return func.HttpResponse(
        json.dumps(response_json),
        status_code=HTTPStatus.OK,
        mimetype="application/json",
    )
