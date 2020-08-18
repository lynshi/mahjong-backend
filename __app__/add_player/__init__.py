import json

import azure.functions as func
import jwt
from loguru import logger

from __app__ import datastore
from __app__ import utils


def main(req: func.HttpRequest, connectionInfoJson: str) -> func.HttpResponse:
    """Add a player to a room by creating appropriate entries in Cosmos and SignalR."""
    logger.info("Adding a new player")

    json_body = utils.request.get_json(req, ("name", "roomCode"))
    player_name = json_body["name"]
    room_code = json_body["roomCode"]

    player_id = datastore.environment.add_user(player_name, room_code)
    room_key = datastore.environment.get_room_key(room_code)

    response_json = json.loads(connectionInfoJson)
    player_id_json = {
        "playerId": player_id,
    }
    response_json = {**response_json, **player_id_json}

    response_json["playerIdToken"] = jwt.encode(
        player_id_json, room_key, algorithm="HS256"
    ).decode("utf-8")

    return func.HttpResponse(
        json.dumps(response_json),
        status_code=200,
        headers={"Content-type": "application/json"},
    )
