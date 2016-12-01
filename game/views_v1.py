from urllib.parse import splitquery

from .models import User
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


@no_auth
class UserView():
    @falcon.after(encode_json)
    def on_get(self, req, resp):
        page, per_page = int(req.get_param("page", default=0)), int(req.get_param("per_page", default=5))
        res = User.slice(page * per_page, (page + 1) * per_page).run()
        resp.json = {'users': list(res.items)}

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

    @auth
    @require(roles='admin')
    @falcon.before(decode_json)
    def on_post(self, req, resp):
        username = req.json.get("username", None)
        first_name = req.json.get("first_name", "")
        last_name = req.json.get("last_name", "")
        if username is None:
            raise falcon.HTTPBadRequest(description="No username specified")
        usr = User.get(username=username)
        if usr is not None:
            return  # already exists, just return an ok
        try:
            usr = User.factory(username, first_name, last_name)
        except:
            raise falcon.HTTPInternalServerError("Exception adding user")
        if usr is None:
            raise falcon.HTTPInvalidParam("User already exists", "username")
        link_base = splitquery(req.url)[0]
        resp.location = "{}/{}/".format(link_base, username)
        resp.status = falcon.HTTP_CREATED


@auth
class UserDetailView():
    def _get_user(self, username):
        usr = User.get(username=username)
        if usr is None:
            raise falcon.HTTPNotFound()
        return usr

    @falcon.after(encode_json)
    def on_get(self, req, resp, username):
        resp.json = self._get_user(username)

    @require(users=SpecialRequire.current_user)
    @falcon.before(decode_json)
    @falcon.after(encode_json)
    def on_put(self, req, resp, username=None):
        usr = User.get(username=username)
        if usr is None:
            raise falcon.HTTPNotFound()
        new_username = req.json.get("username", None)
        first_name = req.json.get("first_name", None)
        last_name = req.json.get("last_name", None)
        if new_username is not None and User.get(username=new_username) is not None:
            raise falcon.HTTPInvalidParam("New user name already exists", "username")
        if new_username is not None:
            usr["username"] = new_username
        if first_name is not None:
            usr["first_name"] = first_name
        if last_name is not None:
            usr["last_name"] = last_name
        usr.save()
        resp.json = self._get_user(username)

    @require(roles='admin')
    def on_delete(self, req, resp, username):
        usr = User.get(username=username)
        if usr is None:
            raise falcon.HTTPNotFound()
        usr.delete()
        resp.status = falcon.HTTP_NO_CONTENT


def views_v1():
    return [(api_prefix, ApiInfoView()),
            (api_prefix + "users/", UserView()),
            (api_prefix + "users/{username}/", UserDetailView()),
            ]