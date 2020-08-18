from dataclasses import dataclass


@dataclass
class Player:
    """Represents a player."""

    id: int
    name: str
    signing_key: str
