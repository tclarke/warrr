from urllib.parse import splitquery

import falcon

from ..models import Board
from ..utils import encode_json, auth, decode_json


@auth
class BoardView:
    @falcon.after(encode_json)
    def on_get(self, req, resp):
        page, per_page = int(req.get_param("page", default=0)), int(req.get_param("per_page", default=5))
        res = Board.slice(page * per_page, (page + 1) * per_page).run()
        resp.json = {'boards': list(res.items)}

        link_base = splitquery(req.uri)[0]
        link_target = "{}{}".format(link_base, falcon.util.to_query_str({'page': 0, 'per_page': per_page}))
        resp.add_link(link_target, 'first')
        last_page = (Board.count() - (1 if Board.count() % per_page == 0 else 0)) // per_page
        if page > 0:
            link_target = "{}{}".format(link_base, falcon.util.to_query_str({'page': page - 1, 'per_page': per_page}))
            resp.add_link(link_target, 'prev')
        if page < last_page:
            link_target = "{}{}".format(link_base, falcon.util.to_query_str({'page': page + 1, 'per_page': per_page}))
            resp.add_link(link_target, 'next')
        link_target = "{}{}".format(link_base, falcon.util.to_query_str({'page': last_page, 'per_page': per_page}))
        resp.add_link(link_target, 'last')

    @falcon.before(decode_json)
    def on_post(self, req, resp):
        try:
            board = Board.factory()
        except Exception as e:
            raise falcon.HTTPInternalServerError("Exception creating board: {}".format(e))
        if board is None:
            raise falcon.HTTPInternalServerError("Unable to create board")
        link_base = splitquery(req.url)[0]
        resp.location = "{}/{}/".format(link_base, board.fields.id)
        resp.status = falcon.HTTP_CREATED


def api(api_prefix):
    return [(api_prefix + "boards/", BoardView()),
            ]
