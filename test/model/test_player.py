# pylint: disable=missing-function-docstring

import jwt
import pytest

from __app__.model import Player


player_id = "0"
player_name = "player0"
room_code = "ABCD"
signing_key = "012345"


@pytest.fixture(name="player")
def fixture_player():
    yield Player(player_id, player_name, room_code, signing_key)


def test_get_jwt(player: Player):
    assert player.get_jwt() == jwt.encode(
        player.to_dict(), signing_key, algorithm=Player.jwt_algorithm
    ).decode("utf-8")


def test_to_dict(player: Player):
    assert player.to_dict() == {
        "playerId": player_id,
        "playerName": player_name,
        "roomCode": room_code,
    }


def test_to_dict_with_jwt(player: Player):
    assert player.to_dict_with_jwt() == {
        **player.to_dict(),
        **{"playerDataToken": player.get_jwt()},
    }


def test_from_jwt(player: Player):
    token = player.get_jwt()
    assert Player.from_jwt(token, signing_key) == player
