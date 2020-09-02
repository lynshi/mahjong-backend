# pylint: disable=missing-function-docstring

from http import HTTPStatus
import json
from unittest.mock import MagicMock, patch

import azure.functions as func
import pytest

from __app__ import model, utils
from __app__.negotiate import main

from . import common


@pytest.fixture(name="action")
def fixture_action():
    yield MagicMock()


connection_info_json = json.dumps({"field": "value"})


def test_negotiate_without_json(action: func.Out):
    json_request = {}
    with patch("__app__.utils.request.get_json") as get_json_mock:
        get_json_mock.side_effect = utils.request.GetJsonError
        request = func.HttpRequest(
            "POST", "/api/negotiate", body=json.dumps(json_request).encode()
        )

        response = main(request, connection_info_json, action)

    get_json_mock.assert_called_once_with(request, ("playerDataToken", "roomCode",))
    action.set.assert_not_called()

    common.validate_response_fields(response)
    assert common.get_json(response) == json.loads(connection_info_json)


def test_negotiate_rejects_invalid_jwt(action: func.Out):
    player = model.Player("0", "player0", "ABCD", "SIGNING KEY")
    json_request = {"roomCode": player.room_code, "playerDataToken": player.get_jwt()}
    with patch("__app__.utils.request.get_json") as get_json_mock:
        get_json_mock.return_value = json_request
        request = func.HttpRequest(
            "POST", "/api/negotiate", body=json.dumps(json_request).encode()
        )

        with patch(
            "__app__.datastore.environment.get_room_signing_key"
        ) as get_signing_key_mock:
            get_signing_key_mock.return_value = f"not {player.room_signing_key}"
            response = main(request, connection_info_json, action)

    get_json_mock.assert_called_once_with(request, ("playerDataToken", "roomCode",))
    get_signing_key_mock.assert_called_once_with(player.room_code)
    action.set.assert_not_called()

    common.validate_response_fields(
        response, status_code=HTTPStatus.FORBIDDEN, mimetype="text/plain"
    )


def test_negotiate_rejects_different_room_code(action: func.Out):
    player = model.Player("0", "player0", "ABCD", "SIGNING KEY")
    other_code = f"not {player.room_code}"
    json_request = {"roomCode": other_code, "playerDataToken": player.get_jwt()}
    with patch("__app__.utils.request.get_json") as get_json_mock:
        get_json_mock.return_value = json_request
        request = func.HttpRequest(
            "POST", "/api/negotiate", body=json.dumps(json_request).encode()
        )

        with patch(
            "__app__.datastore.environment.get_room_signing_key"
        ) as get_signing_key_mock:
            get_signing_key_mock.return_value = player.room_signing_key
            response = main(request, connection_info_json, action)

    get_json_mock.assert_called_once_with(request, ("playerDataToken", "roomCode",))
    get_signing_key_mock.assert_called_once_with(other_code)
    action.set.assert_not_called()

    common.validate_response_fields(
        response, status_code=HTTPStatus.FORBIDDEN, mimetype="text/plain"
    )


def test_negotiate_adds_player_to_group(action: func.Out):
    player = model.Player("0", "player0", "ABCD", "SIGNING KEY")
    json_request = {"roomCode": player.room_code, "playerDataToken": player.get_jwt()}
    with patch("__app__.utils.request.get_json") as get_json_mock:
        get_json_mock.return_value = json_request
        request = func.HttpRequest(
            "POST", "/api/negotiate", body=json.dumps(json_request).encode()
        )

        with patch(
            "__app__.datastore.environment.get_room_signing_key"
        ) as get_signing_key_mock:
            get_signing_key_mock.return_value = player.room_signing_key
            response = main(request, connection_info_json, action)

    get_json_mock.assert_called_once_with(request, ("playerDataToken", "roomCode",))
    get_signing_key_mock.assert_called_once_with(player.room_code)
    action.set.assert_called_once_with(
        json.dumps(
            {"userId": player.id, "groupName": player.room_code, "action": "add"}
        )
    )

    common.validate_response_fields(response)
    assert common.get_json(response) == json.loads(connection_info_json)
