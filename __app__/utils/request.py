"""Utility functions for validation tasks."""
from typing import Dict, Iterable

import azure.functions as func


class JsonNotPresent(Exception):
    """Raise when the request has no JSON."""


class MissingRequiredField(Exception):
    """Raise when the request is missing some required field."""

    def __init__(self, field_name: str):
        super().__init__(f"Missing required field {field_name}")


def get_json(req: func.HttpRequest, required_fields: Iterable[str]) -> Dict:
    def _ensure_required_fields_present(
        json_body: Dict, required_fields: Iterable[str]
    ):
        for field in required_fields:
            if field not in json_body:
                raise MissingRequiredField(field)

    try:
        json_body = req.get_json()
    except ValueError:
        raise JsonNotPresent()

    _ensure_required_fields_present(json_body, required_fields)
    return json_body
