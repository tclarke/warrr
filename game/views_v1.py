import falcon
import json
from urllib.parse import splitquery

from .models import User

__version__ = (1, 0, 0)
__api_version__ = __version__[0]
__version_str__ = ".".join(map(str, __version__))
api_prefix = "/api/v{}/".format(__api_version__)

class RemodelJSONEncoder(json.JSONEncoder):
    def default(self, o):
        from remodel.models import Model
        if isinstance(o, Model):
            return o.fields.as_dict()
        return json.JSONEncoder.default(self, o)

class ApiInfoView():
    def on_get(self, req, resp):
       resp.body = json.dumps({'version': str(__api_version__)})
       resp.content_type = "application/json"

class UserView():
    def on_get(self, req, resp):
        page, per_page = int(req.get_param("page", default=0)), int(req.get_param("per_page", default=5))
        all_users = User.all()
        res = all_users.query.slice(page*per_page, (page+1)*per_page).run()
        resp.body = json.dumps({'users': list(res.items)})
        resp.content_type = "application/json"
        link_base = splitquery(req.uri)[0]
        link_target = "{}{}".format(link_base, falcon.util.to_query_str({'page': 0, 'per_page': per_page}))
        resp.add_link(link_target, 'first')
        last_page = (User.count() - (1 if User.count() % per_page == 0 else 0)) // per_page
        if page > 0:
            link_target = "{}{}".format(link_base, falcon.util.to_query_str({'page': page-1, 'per_page': per_page}))
            resp.add_link(link_target, 'prev')
        if page < last_page:
            link_target = "{}{}".format(link_base, falcon.util.to_query_str({'page': page+1, 'per_page': per_page}))
            resp.add_link(link_target, 'next')
        link_target = "{}{}".format(link_base, falcon.util.to_query_str({'page': last_page, 'per_page': per_page}))
        resp.add_link(link_target, 'last')

    def on_post(self, req, resp):
        if req.content_type != "application/json":
            raise falcon.HTTPUnsupportedMediaType("application/json required")
        username = None
        if req.content_length > 0:
            data = json.loads(req.stream.read().decode('utf-8'))
            username = data.get("username", None)
            first_name = data.get("first_name", "")
            last_name = data.get("last_name", "")
        if username is None:
            raise falcon.HTTPBadRequest(description="No username specified")
        usr = User.get(username=username)
        if usr is not None:
            return  # already exists, just return an ok
        try:
            usr = User.factory(username, first_name, last_name)
        except:
            import logging
            logging.exception("Create")
            raise falcon.HTTPInternalServerError("Exception adding user")
        if usr is None:
            raise falcon.HTTPInvalidParam("User already exists", "username")
        link_base = splitquery(req.url)[0]
        resp.location = "{}/{}/".format(link_base, username)
        resp.status = falcon.HTTP_CREATED


class UserDetailView():
    def on_get(self, req, resp, username):
        usr = User.get(username=username)
        if usr is None:
            raise falcon.HTTPNotFound()
        if not req.client_accepts_json:
            req.log_error("Client will not accept json")
            raise falcon.HTTPNotAcceptable("Client must accept application/json")
        resp.body = json.dumps(usr, cls=RemodelJSONEncoder)
        resp.content_type = "application/json"

    def on_put(self, req, resp, username):
        usr = User.get(username=username)
        if usr is None:
            raise falcon.HTTPNotFound()
        if req.content_type != "application/json":
            raise falcon.HTTPUnsupportedMediaType("application/json required")
        if req.content_length > 0:
            data = json.loads(req.stream.read().decode('utf-8'))
            new_username = data.get("username", None)
            first_name = data.get("first_name", None)
            last_name = data.get("last_name", None)
        if new_username is not None and User.get(username=new_username) is not None:
            raise falcon.HTTPInvalidParam("New user name already exists", "username")
        if new_username is not None:
            usr["username"] = new_username
        if first_name is not None:
            usr["first_name"] = first_name
        if last_name is not None:
            usr["last_name"] = last_name
        usr.save()
        self.on_get(req, resp, username)

    def on_delete(self, req, resp, username):
        usr = User.get(username=username)
        if usr is None:
            raise falcon.HTTPNotFound()
        usr.delete()
        resp.status = falcon.HTTP_NO_CONTENT


def views_v1():
    return [(api_prefix, ApiInfoView()),
            (api_prefix + "user/", UserView()),
            (api_prefix + "user/{username}/", UserDetailView()),
           ]