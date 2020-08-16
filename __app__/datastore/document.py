# pylint: disable=missing-function-docstring

from typing import Dict

from bson.objectid import ObjectId

class UnknownField(Exception):
    """Raised when a document contains an unknown field."""


class Room:
    """Class representing a document in the 'rooms' collection."""
    def __init__(self, document: Dict):
        self._document = Room.validate_fields(document)

    @property
    def document(self) -> Dict:
        return self._document

    @property
    def id(self) -> ObjectId:
        return self._document["_id"]

    @staticmethod
    def validate_fields(document: Dict) -> Dict:
        """Ensures the document contains fields that are expected.

        Raises an exception if any field is unexpected, otherwise returns the document."""
        known_fields = {
            '_id'
        }

        for key in document:
            if key not in known_fields:
                raise UnknownField(key)

        return document
