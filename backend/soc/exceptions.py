import logging
from pathlib import Path
from traceback import walk_tb
from rest_framework.views import exception_handler
from rest_framework.response import Response
logger = logging.getLogger(__name__)

def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        # Database exception messages can contain SQL values and personal data.
        # Keep code locations, but never log messages, source lines or frame locals.
        frames = ' -> '.join(
            f'{Path(frame.f_code.co_filename).name}:{lineno}:{frame.f_code.co_name}'
            for frame, lineno in walk_tb(exc.__traceback__)
        )
        view = context.get('view')
        logger.error(
            'Unhandled API error type=%s view=%s frames=%s',
            type(exc).__name__, type(view).__name__, frames,
        )
        return Response({'error': {'detail': 'The service could not complete this request. Please retry.'}, 'status': 500}, status=500)
    response.data = {'error': response.data, 'status': response.status_code}
    return response
