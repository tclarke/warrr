import logging

import hug
from falcon_cors import CORS

log = logging.getLogger("falcon_cors")
log.setLevel(logging.DEBUG)

cors = CORS(allow_all_origins=True, allow_all_headers=True, allow_all_methods=True)
api = hug.API(__name__)
api.http.add_middleware(cors.middleware)
api.http.output_format = hug.output_format.pretty_json


@hug.get('/', versions=1)
def api_info_view(docs: hug.directives.documentation):
    return docs


@hug.extend_api()
def api():
    from .views import __all__ as views
    return views
