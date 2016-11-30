import json

import falcon


class RemodelJSONEncoder(json.JSONEncoder):
    def default(self, o):
        from remodel.models import Model
        if isinstance(o, Model):
            return o.fields.as_dict()
        return json.JSONEncoder.default(self, o)


def encode_json(req, resp, *args):
    if 'json' not in resp.__dict__:
        raise falcon.HTTPInternalServerError("Unable to encode json")
    if not req.client_accepts_json:
        raise falcon.HTTPNotAcceptable("Client must accept application/json")
    resp.body = json.dumps(resp.json, cls=RemodelJSONEncoder)
    resp.content_type = "application/json"


def decode_json(req, *args):
    if req.content_type != "application/json":
        raise falcon.HTTPUnsupportedMediaType("application/json required")
    if req.content_length > 0:
        req.json = json.loads(req.stream.read().decode('utf-8'))
    else:
        req.json = {}
