# pylint: disable=missing-function-docstring

import json

import azure.functions as func
import pytest

from __app__ import utils


def test_MissingRequiredField_message():
    field = "a field"
    assert (
        str(utils.request.MissingRequiredField(field))
        == f"Missing required field {field}"
    )


def test_get_json():
    json_body = {"field0": 0, "field1": 1}

    request = func.HttpRequest(
        "POST", "/api/random", body=json.dumps(json_body).encode()
    )

    assert utils.request.get_json(request, ("field0", "field1")) == json_body


def test_get_json_raises_MissingRequiredField():
    json_body = {"field0": 0}

    request = func.HttpRequest(
        "POST", "/api/random", body=json.dumps(json_body).encode()
    )

    with pytest.raises(utils.request.MissingRequiredField):
        utils.request.get_json(request, ("field0", "field1"))


def test_get_json_raises_JsonNotPresent():
    request = func.HttpRequest("POST", "/api/random", body="".encode())

    with pytest.raises(utils.request.JsonNotPresent):
        utils.request.get_json(request, ("field0", "field1"))
