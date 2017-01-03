from urllib.parse import splitquery

import falcon

from ..models import Piece
from ..utils import encode_json, no_auth


@no_auth
class PieceView:
    @falcon.after(encode_json)
    def on_get(self, req, resp):
        page, per_page = int(req.get_param("page", default=0)), int(req.get_param("per_page", default=5))
        if per_page < 0:
            resp.json = {'pieces': list(Piece.objects.all())}
        else:
            res = Piece.slice(page * per_page, (page + 1) * per_page).run()
            resp.json = {'pieces': list(res.items)}

            link_base = splitquery(req.uri)[0]
            link_target = "{}{}".format(link_base, falcon.util.to_query_str({'page': 0, 'per_page': per_page}))
            resp.add_link(link_target, 'first')
            last_page = (Piece.count() - (1 if Piece.count() % per_page == 0 else 0)) // per_page
            if page > 0:
                link_target = "{}{}".format(link_base,
                                            falcon.util.to_query_str({'page': page - 1, 'per_page': per_page}))
                resp.add_link(link_target, 'prev')
            if page < last_page:
                link_target = "{}{}".format(link_base,
                                            falcon.util.to_query_str({'page': page + 1, 'per_page': per_page}))
                resp.add_link(link_target, 'next')
            link_target = "{}{}".format(link_base, falcon.util.to_query_str({'page': last_page, 'per_page': per_page}))
            resp.add_link(link_target, 'last')


def api(api_prefix):
    return [(api_prefix + "pieces/", PieceView()),
            ]
