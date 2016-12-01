import json
from enum import Enum
from functools import wraps

import falcon
from talons.auth import middleware, basicauth, external

from .models import user_authenticate


class RemodelJSONEncoder(json.JSONEncoder):
    def default(self, o):
        from remodel.models import Model
        if isinstance(o, Model):
            return o.fields.as_dict()
        return json.JSONEncoder.default(self, o)


def encode_json(req, resp, resource):
    if 'json' not in resp.__dict__:
        raise falcon.HTTPInternalServerError("Unable to encode json")
    if not req.client_accepts_json:
        raise falcon.HTTPNotAcceptable("Client must accept application/json")
    resp.body = json.dumps(resp.json, cls=RemodelJSONEncoder)
    resp.content_type = "application/json"


def decode_json(req, resp, resource, params):
    if req.content_type != "application/json":
        raise falcon.HTTPUnsupportedMediaType("application/json required")
    if req.content_length > 0:
        req.json = json.loads(req.stream.read().decode('utf-8'))
    else:
        req.json = {}


def authorize(ident, users, roles, groups, username):
    # if we specify a list of users allowed, match any of them
    user_found = (users is not None) and ident.login in users
    if (users is not None) and (
        username is not None) and SpecialRequire.current_user in users and username == ident.login:
        user_found = True

    # if we specify and groups or roles, match any of them
    group_found = (groups is not None) and len(set(ident.groups).intersection(set(groups))) > 0
    role_found = (roles is not None) and len(set(ident.roles).intersection(set(roles))) > 0

    # succeed if we match anything anywhere. if you need to match multiple, use the decorator more than once
    return user_found or group_found or role_found


class SpecialRequire(Enum):
    current_user = 1


def require(users=None, roles=None, groups=None, current_user_key='username'):
    users = (users,) if isinstance(users, str) or isinstance(users, SpecialRequire) else users
    groups = (groups,) if isinstance(groups, str) else groups
    roles = (roles,) if isinstance(roles, str) else roles

    def wrap(fn):
        @wraps(fn)
        def check_auth(obj, req, *args, **kargs):
            ident = req.env.get('wsgi.identity', None)
            username = kargs.get(current_user_key, None)
            if (ident is not None) and not authorize(ident, users, roles, groups, username):
                raise falcon.HTTPForbidden("Action not allowed",
                                           "The specified user does not have authorization to perform this action",
                                           headers={'WWW-Authenticate': 'Basic realm="Game"'})
            return fn(obj, req, *args, **kargs)

        return check_auth

    return wrap


def auth(fn):
    fn.use_auth = True
    return fn


def no_auth(fn):
    fn.use_auth = False
    return fn


class AuthMiddleware:
    def __init__(self, **config):
        if 'external_authn_callable' not in config:
            config['external_authn_callable'] = user_authenticate
            config['external_sets_roles'] = True
        if 'default_authorize' not in config:
            config['default_authorize'] = True  # we'll use more fine grained authorization with decorators
        self._talon_mw = middleware.create_middleware(identify_with=[basicauth.Identifier],
                                                      authenticate_with=external.Authenticator,
                                                      **config)

    def process_resource(self, req, resp, resource, params):
        default = getattr(resource, 'use_auth', True)
        func = getattr(resource, "on_{}".format(req.method.lower()), None)
        if func is None and default is False:  # no func override and don't use auth by default
            return True
        if func is not None and getattr(func, 'use_auth', default) is False:  # func override says don't use auth
            return
        try:
            rval = self._talon_mw(req, resp, params)
        except falcon.HTTPForbidden:
            raise falcon.HTTPForbidden("Forbidden",
                                       "The specified user does not have authorization to perform this action",
                                       headers={'WWW-Authenticate': 'Basic realm="Game"'})
        except falcon.HTTPUnauthorized:
            raise falcon.HTTPUnauthorized("Authentication required",
                                          "Authentication required",
                                          headers={'WWW-Authenticate': 'Basic realm="Game"'})
        return rval
