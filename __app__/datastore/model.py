from dataclasses import dataclass


@dataclass
class Player:
    """Represents a player."""

    id: int
    key: str
    name: str
