from dataclasses import dataclass


@dataclass
class Player:
    """Represents a player."""

    id: str
    name: str
    signing_key: str
