# pylint: disable=missing-function-docstring
from unittest.mock import MagicMock, patch

import pymongo
import pytest

from __app__ import datastore


def test_create_room():
    room_code = 'ABCD'
    with patch('__app__.datastore.environment.MongoClient') as init_mock:
        client_mock = MagicMock()
        init_mock.return_value = client_mock

        datastore.environment.create_room(room_code)

    init_mock.assert_called_once_with(datastore.COSMOS_CONNECTION_STRING)

    client_mock.mahjong.rooms.insert_one.assert_called_once_with({
        '_id': room_code,
    })


def test_create_room_catches_duplicate_key():
    room_code = 'ABCD'
    with patch('__app__.datastore.environment.MongoClient') as init_mock:
        client_mock = MagicMock()
        init_mock.return_value = client_mock

        client_mock.mahjong.rooms.insert_one.side_effect = pymongo.errors.DuplicateKeyError('na')

        with pytest.raises(datastore.environment.RoomCodeExists):
            datastore.environment.create_room(room_code)

    init_mock.assert_called_once_with(datastore.COSMOS_CONNECTION_STRING)

    client_mock.mahjong.rooms.insert_one.assert_called_once_with({
        '_id': room_code,
    })
