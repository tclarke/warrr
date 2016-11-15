import falcon
import os.path
import mimetypes
import logging

app = falcon.API()

# development server for static data, probably better to use a proper webserver like nginx or apache for production
class StaticSink():
    """Basic static data server for use during development"""
    def __init__(self, static_path):
        mimetypes.init()
        self.static_path = static_path

    def __call__(self, req, resp):
        if req.path == '/' or len(req.path) == 0:
            req.path = "/index.html"
        if req.path[0] == '/':
            req.path = req.path[1:]
        pth = os.path.join(self.static_path, req.path)
        logging.debug(pth)
        if os.path.isfile(pth):
            typ, enc = mimetypes.guess_type(pth)
            if typ is None:
                typ = 'application/octet-stream'
            logging.debug(typ)
            resp.content_type = typ
            resp.body = open(pth).read()
        else:
            raise falcon.HTTPNotFound()

static = StaticSink(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static")))
app.add_sink(static, '/')