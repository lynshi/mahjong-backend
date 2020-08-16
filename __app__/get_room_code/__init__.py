import json
import random

import azure.functions as func
from loguru import logger


def main(req: func.HttpRequest) -> func.HttpResponse:
    logger.info('Processing "get_room_code" request.')

    room_code_response = {
        'code': ''.join([chr(ord('A') + random.randint(0, 26)) for _ in range(4)])
    }

    return func.HttpResponse(
        json.dumps(room_code_response),
        status_code=200,
        mimetype='application/json'
    )
