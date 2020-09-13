from http import HTTPStatus

import azure.functions as func
import jwt
from loguru import logger

from __app__ import datastore, model, utils


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Help a player enter a lobby by returning all known lobby data."""
    logger.info("Enter a lobby")

    try:
        json_body = utils.request.get_json(req, ("playerDataToken", "roomCode"))
    except utils.request.GetJsonError:
        logger.opt(exception=True).error("Error getting JSON")
        return func.HttpResponse("JSON error", status_code=HTTPStatus.BAD_REQUEST,)

    room_code = json_body["roomCode"]
    player_data_token = json_body["playerDataToken"]

    room_key = datastore.environment.get_room_signing_key(room_code)

    try:
        player = model.Player.from_jwt(player_data_token, room_key)
    except jwt.InvalidTokenError:
        return func.HttpResponse(status_code=HTTPStatus.FORBIDDEN)

    if player.room_code != room_code:
        return func.HttpResponse(status_code=HTTPStatus.FORBIDDEN)
