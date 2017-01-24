from urllib.parse import splitquery

import aiohttp
import falcon.util
import hug

import auth
from ..models import Board, Piece


@hug.get('/boards/', versions=1)
def board_view_get(page: hug.types.number = 0, per_page: hug.types.number = 5, request=None, response=None):
    """Get a list of all boards currently stored."""

    res = Board.slice(page * per_page, (page + 1) * per_page).run()

    link_base = splitquery(request.uri)[0]
    link_target = "{}{}".format(link_base, falcon.util.to_query_str({'page': 0, 'per_page': per_page}))
    response.add_link(link_target, 'first')
    last_page = (Board.count() - (1 if Board.count() % per_page == 0 else 0)) // per_page
    if page > 0:
        link_target = "{}{}".format(link_base, falcon.util.to_query_str({'page': page - 1, 'per_page': per_page}))
        response.add_link(link_target, 'prev')
    if page < last_page:
        link_target = "{}{}".format(link_base, falcon.util.to_query_str({'page': page + 1, 'per_page': per_page}))
        response.add_link(link_target, 'next')
    link_target = "{}{}".format(link_base, falcon.util.to_query_str({'page': last_page, 'per_page': per_page}))
    response.add_link(link_target, 'last')
    return {'boards': list(res.items)}


@hug.post('/boards/', versions=1, requires=auth.token_authentication)
def board_view_post(user: hug.directives.user, body=None, request=None, response=None):
    """Create a new board with a specified rules URL."""

    if not user:
        raise falcon.HTTPUnauthorized("Invalid user", "User must be logged in to create a board.")
    if 'create' not in user['roles']:
        raise falcon.HTTPUnauthorized("Insufficient roles",
                                      "This operation requires the 'create' role which user {0} does not have.".format(
                                          user['username']))
    if body is None or body == "" or "rules_url" not in body:
        raise falcon.HTTPInvalidParam("Must specify a rules_url", "rules_url")
    try:
        board = Board.factory()
    except Exception as e:
        response.status = falcon.HTTP_500
        raise falcon.HTTPInternalServerError("Exception creating board: {}".format(e))
    if board is None:
        raise falcon.HTTPInternalServerError("Unable to create board")
    board['rules_url'] = body["rules_url"]
    board.save()
    link_base = splitquery(request.url)[0]
    response.location = "{}/{}/".format(link_base, board['id'])
    response.status = falcon.HTTP_CREATED
    return board.fields.as_dict()


@hug.get("/boards/{board_id}/")
def get_board_configuration(board_id: hug.types.uuid):
    """Get the board state object for the specified board ID"""

    board = Board.get(id=board_id)
    if board is None:
        raise falcon.HTTPNotFound()
    return board.fields.as_dict()


@hug.put("/boards/{board_id}/")
async def update_board_configuration(board_id: hug.types.uuid, body, response):
    """Board piece positions and validate with the rules service."""

    board = Board.get(id=board_id)
    if board is None:
        raise falcon.HTTPNotFound()
    friendly = [(p['location'], Piece.get(p['id'])) for p in body.get("friendly", [])]
    neutral = [(p['location'], Piece.get(p['id'])) for p in body.get("neutral", [])]
    hostile = [(p['location'], Piece.get(p['id'])) for p in body.get("hostile", [])]
    board.reset()
    board.add_pieces(friendly, 'friendly')
    board.add_pieces(neutral, 'neutral')
    board.add_pieces(hostile, 'hostile')
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(board.get('rules_url', ''), data=board.fields.as_dict()) as resp:
                if resp.status == 200:
                    board['valid'] = True
                    board.save()
                    board = board.fields.as_dict()
                else:
                    response.status = falcon.__dict__.get('HTTP_{0}'.format(resp.status),
                                                          falcon.HTTPInternalServerError)
                    board = {'url': board.get('rules_url', '')}
        except Exception as e:
            raise falcon.HTTPServiceUnavailable("Rules resource unavailable",
                                                str(e),
                                                300)
    return board
