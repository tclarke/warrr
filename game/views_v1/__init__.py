from . import user, board


def api(api_prefix):
    return user.api(api_prefix) + \
           board.api(api_prefix)
