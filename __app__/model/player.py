from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar, Dict

import jwt


@dataclass
class Player:
    """Represents a player."""

    id: str
    name: str
    room_code: str
    room_signing_key: str

    jwt_algorithm: ClassVar[str] = "HS256"

    def get_jwt(self) -> str:
        """Generate JWT token from data."""
        player_data = self.to_dict()
        return jwt.encode(
            player_data, self.room_signing_key, algorithm=Player.jwt_algorithm
        ).decode("utf-8")

    def to_dict_with_jwt(self) -> Dict:
        """Get a dictionary with a JWT for the claims."""
        player_data = self.to_dict()
        player_data["playerDataToken"] = self.get_jwt()
        return player_data

    def to_dict(self) -> Dict:
        """Generate a dictionary from data."""
        return {
            "playerId": self.id,
            "playerName": self.name,
            "roomCode": self.room_code,
        }

    @staticmethod
    def from_jwt(token: str, secret: str) -> Player:
        """Generate a Player from a JWT."""
        decoded = jwt.decode(token, secret, algorithms=Player.jwt_algorithm)
        return Player(
            decoded["playerId"], decoded["playerName"], decoded["roomCode"], secret
        )
