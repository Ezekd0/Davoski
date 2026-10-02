import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
logger = logging.getLogger(__name__)

def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        logger.error('Unhandled API error', exc_info=(type(exc), exc, exc.__traceback__))
        return Response({'error': {'detail': 'The service could not complete this request. Please retry.'}, 'status': 500}, status=500)
    response.data = {'error': response.data, 'status': response.status_code}
    return response
