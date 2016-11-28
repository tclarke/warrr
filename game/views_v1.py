import falcon
import json

__version__ = (1, 0, 0)
__api_version__ = __version__[0]
__version_str__ = ".".join(map(str, __version__))

class ApiInfo():
    def on_get(self, req, resp):
       resp.data = json.dumps({'version': str(__api_version__)}).encode('utf-8')
       resp.content_type = "application/json"

def views_v1():
    return [("/api/v%d/" % __api_version__, ApiInfo())]