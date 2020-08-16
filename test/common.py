import json
from typing import Dict

import azure.functions as func


def json_to_bytes(json_body: Dict) -> bytes:
    """Convert a dictionary to bytes."""
    json_str = json.dumps(json_body)
    return json_str.encode("utf-8")


def get_json(response: func.HttpResponse) -> Dict:
    """Get JSON from an HttpResponse."""
    return json.loads(response.get_body().decode('utf-8'))
