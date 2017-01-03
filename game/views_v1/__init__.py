from . import user, board, piece


def api(api_prefix):
    return user.api(api_prefix) + \
           board.api(api_prefix) + \
           piece.api(api_prefix)
