from importlib import import_module

from .utils import *

__version__ = (1, 0, 0)
__api_version__ = __version__[0]
__version_str__ = ".".join(map(str, __version__))
api_prefix = "/api/v{}/".format(__api_version__)


@no_auth
class ApiInfoView():
    @falcon.after(encode_json)
    def on_get(self, req, resp):
        resp.json = {'version': str(__api_version__)}


def api():
    current = import_module(".views_v{}".format(__api_version__), __package__)
    rval = [(api_prefix, ApiInfoView())]
    rval += current.api(api_prefix)
    return rval
