import hug
import jwt


def token_verify(token):
    # this is the secret API key for sharing data between this microservice and the other ones
    # it's necessary to get auth info from jwt. Normally, this would be in a server config file
    # but this is an example so we'll hard code it here
    secret_key = 'this-is-the-microservice-to-microservice-secret'
    # verify a token is valid and decode it
    try:
        method, token = token.split(' ')
        if method.lower() != 'bearer':
            return False
        return jwt.decode(token, secret_key, algorithm='HS256')
    except jwt.DecodeError:
        return False


token_authentication = hug.authentication.token(token_verify)
