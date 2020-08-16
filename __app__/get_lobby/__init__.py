from http import HTTPStatus

import azure.functions as func
from loguru import logger

from __app__ import utils


def main(req: func.HttpRequest) -> func.HttpResponse:
    logger.info('Getting lobby')

    try: 
        request_json = req.get_json()
    except ValueError:
        return func.HttpResponse(
            "Missing JSON body",
            status_code=HTTPStatus.BAD_REQUEST
        )

    try:
        utils.validate.ensure_required_fields_present(request_json, ['roomCode'])
    except ValueError:
        logger.opt(exception=True).error("failed to validate request")
        return func.HttpResponse(
            status_code=HTTPStatus.BAD_REQUEST
        )

    room_code = request_json["roomCode"]

    return func.HttpResponse(
            "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
            status_code=200
    )
