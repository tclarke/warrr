from urllib.parse import splitquery

import falcon.util
import hug

from game.models import Piece


@hug.get("/pieces/", versions=1)
def piece_view_get(page: hug.types.number = 0, per_page: hug.types.number = 5, request=None, response=None):
    """Get a list of all available pieces including the IDs and icon URLs."""

    resp_body = {}
    if per_page < 0:
        resp_body['pieces'] = [p.fields.as_dict() for p in Piece.objects.all()]
    else:
        res = Piece.slice(page * per_page, (page + 1) * per_page).run()
        resp_body['pieces'] = list(res.items)

        link_base = splitquery(request.uri)[0]
        link_target = "{}{}".format(link_base, falcon.util.to_query_str({'page': 0, 'per_page': per_page}))
        response.add_link(link_target, 'first')
        last_page = (Piece.count() - (1 if Piece.count() % per_page == 0 else 0)) // per_page
        if page > 0:
            link_target = "{}{}".format(link_base,
                                        falcon.util.to_query_str({'page': page - 1, 'per_page': per_page}))
            response.add_link(link_target, 'prev')
        if page < last_page:
            link_target = "{}{}".format(link_base,
                                        falcon.util.to_query_str({'page': page + 1, 'per_page': per_page}))
            response.add_link(link_target, 'next')
        link_target = "{}{}".format(link_base, falcon.util.to_query_str({'page': last_page, 'per_page': per_page}))
        response.add_link(link_target, 'last')
    return resp_body
