from http import HTTPStatus
import json

import azure.functions as func
import jwt
from loguru import logger

from __app__ import datastore, model, utils


def main(
    req: func.HttpRequest, connectionInfoJson: str, action: func.Out
) -> func.HttpResponse:
    """Get SignalR connection info after validating user ID."""
    logger.info("Creating new SignalR connection")

    try:
        json_body = utils.request.get_json(req, ("playerDataToken", "roomCode"))
    except utils.request.GetJsonError:
        # Missing fields suggests this is the SignalR client connecting with an Azure token.
        return func.HttpResponse(
            connectionInfoJson, status_code=HTTPStatus.OK, mimetype="application/json"
        )

    room_code = json_body["roomCode"]
    player_data_token = json_body["playerDataToken"]

    room_key = datastore.environment.get_room_signing_key(room_code)

    try:
        player = model.Player.from_jwt(player_data_token, room_key)
    except jwt.InvalidTokenError:
        return func.HttpResponse(status_code=HTTPStatus.FORBIDDEN)

    if player.room_code != room_code:
        return func.HttpResponse(status_code=HTTPStatus.FORBIDDEN)

    # Add player to group. The group is created automatically if it does not yet exist.
    action.set(
        json.dumps(
            {"userId": player.id, "groupName": player.room_code, "action": "add"}
        )
    )

    return func.HttpResponse(
        connectionInfoJson, status_code=HTTPStatus.OK, mimetype="application/json"
    )
