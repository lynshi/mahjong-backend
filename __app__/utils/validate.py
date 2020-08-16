"""Utility functions for validation tasks."""
from typing import Dict, Iterable


def request(json_body: Dict, required_fields: Iterable[str]):
    """Validate that the dictionary includes all fields required. If not, raises ValueError."""
    for field in required_fields:
        if field not in json_body:
            raise ValueError(f"Request missing required field '{field}' in JSON")
