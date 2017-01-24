#!/usr/bin/env python
import auth
import hashlib
import hug
import logging
import os
from remodel.connection import pool
from remodel.models import Model

pool.configure(db='user')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# basic remodel User model..could do this in straight rethinkdb but we'll be consistent
class User(Model):
    pass


# support functions
def hash_password(password, salt):
    """
    Securely hash a password using a provided salt
    :param password:
    :param salt:
    :return: Hex encoded SHA512 hash of provided password
    """
    password = str(password).encode('utf-8')
    salt = str(salt).encode('utf-8')
    return hashlib.sha512(password + salt).hexdigest()


def authenticate_user(username, password):
    """
    Authenticate a username and password against our database
    :param username:
    :param password:
    :return: authenticated username
    """
    user = User.get(username=username)

    if not user:
        logger.warning("User %s not found", username)
        return False

    if user['password'] == hash_password(password, user['salt']):
        return user

    return False

# basic is only for the /login path, other microservices should user token
basic_authentication = hug.authentication.basic(authenticate_user)


# API endpoints
@hug.get('/verify', requires=auth.token_authentication)
def get_token(user: hug.directives.user):
    """Verify a token is valid by returning a message with the username and available roles."""
    return 'You are user: {0} with roles {1}'.format(user['user'], user['roles'])


@hug.get('/login', requires=basic_authentication)
def token_login(user: hug.directives.user):
    """Login using basic authentication against the database.
       Returns a JWT that can be used to authenticate against other microservices. These other
       services do not need access to the user database. Think of this sort of like a kerberos TGT.
    """
    if user:
        return {'token': jwt.encode({'user': user['username'], 'roles': user['roles']}, secret_key, algorithm='HS256')}
    return 'Invalid username/password'


# cli helpers
@hug.cli("init")
def init_database():
    """Initialize the user database from scratch"""
    from remodel.helpers import create_tables, create_indexes
    from remodel.registry import index_registry
    import rethinkdb as r
    import logging

    logging.basicConfig(level=logging.INFO)
    with pool.get() as conn:
        logging.info("Drop old db")
        try:
            r.db_drop('user').run(conn)
        except:
            pass
        logging.info("Create db")
        r.db_create('user').run(conn)

    logging.info("Create tables")
    create_tables()
    logging.info("Register secondary indices")
    index_registry.register("User", "username")
    index_registry.register("User", "api_key")
    logging.info("Create indices")
    create_indexes()


@hug.cli()
def add_user(username, password, roles=''):
    """
    CLI Parameter to add a user to the database
    :param username:
    :param password:
    :return: JSON status output
    """
    roles = [role.strip() for role in roles.split(',')]
    user = User.get(username=username)
    if user:
        return {
            'error': 'User {0} already exists'.format(username)
        }
    salt = hashlib.sha512(str(os.urandom(64)).encode('utf-8')).hexdigest()
    password = hash_password(password, salt)
    user = User.create(username=username, password=password, salt=salt, roles=roles)
    return {
       'result': 'success',
       'eid': user['id'],
       'user_created': user
    }


if __name__ == '__main__':
    add_user.interface.cli()
    #init_database.interface.cli()
