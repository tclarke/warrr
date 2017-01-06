from urllib.parse import splitquery

import aiohttp
import asyncio
import falcon

from ..models import Board, Piece
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

    @falcon.after(encode_json)
    @falcon.before(decode_json)
    def on_post(self, req, resp):
        try:
            board = Board.factory()
        except Exception as e:
            raise falcon.HTTPInternalServerError("Exception creating board: {}".format(e))
        if board is None:
            raise falcon.HTTPInternalServerError("Unable to create board")
        board['rules_url'] = req.json["rules_url"]
        link_base = splitquery(req.url)[0]
        resp.json = board
        resp.location = "{}/{}/".format(link_base, board['id'])
        resp.status = falcon.HTTP_CREATED

@auth
class BoardDetailView:
    @falcon.after(encode_json)
    @falcon.before(decode_json)
    async def on_put(self, req, resp, board_id):
        board = Board.get(id=board_id)
        if board is None:
            raise falcon.HTTPNotFound()
        friendly = [(p['location'], Piece.get(p['id'])) for p in req.json.get("friendly", [])]
        neutral = [(p['location'], Piece.get(p['id'])) for p in req.json.get("neutral", [])]
        hostile = [(p['location'], Piece.get(p['id'])) for p in req.json.get("hostile", [])]
        board.reset()
        board.add_pieces(friendly, 'friendly')
        board.add_pieces(neutral, 'neutral')
        board.add_pieces(hostile, 'hostile')
        try:
            future = asyncio.Future()
            await asyncio.ensure_future(BoardDetailView.validate(future, board))
            status = future.result()
            if status == 200:
                resp.json = board
            else:
                resp.status = status
        except Exception as e:
            raise falcon.HTTPServiceUnavailable(e)

    @staticmethod
    async def validate(future, board):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(board.get('rules_url', '') + "validation/") as resp:
                    if resp.status == 200:
                        board['valid'] = True
                        board.save()
                    future.set_result(resp.status)
        except Exception as e:
            future.set_exception(e)


def api(api_prefix):
    return [(api_prefix + "boards/", BoardView()),
            (api_prefix + "boards/{board_id}/", BoardDetailView())
            ]
