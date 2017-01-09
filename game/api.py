import hug
from falcon_cors import CORS

cors = CORS(allow_all_origins=True)
api = hug.API(__name__)
api.http.add_middleware(cors.middleware)
api.http.output_format = hug.output_format.pretty_json


@hug.get('/', versions=1)
def api_info_view():
    return {'version': "1.0.0"}


@hug.extend_api()
def api():
    from .views import __all__ as views
    return views
