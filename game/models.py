#!/usr/bin/env python
from remodel.connection import pool
from remodel.models import Model

pool.configure(db='game')


class Piece(Model):
    belongs_to = ('State',)

    @staticmethod
    def factory(name, dist, image_urls):
        return Piece.create(name=name, dist=dist, image_urls=image_urls)


class User(Model):
    belongs_to = ('State', 'Game')

    @staticmethod
    def factory(username, first_name="", last_name="", roles=list()):
        return User.create(username=username, first_name=first_name, last_name=last_name, roles=roles)


def user_authenticate(ident):
    user_rec = User.get(username=ident.login)
    if user_rec is None:
        return False
    if 'roles' in user_rec:
        ident.roles.update(user_rec['roles'])
    if 'groups' in user_rec:
        ident.groups.update(user_rec['groups'])
    return True


class State(Model):
    belongs_to = ('Game',)
    has_many = ('Piece',)
    has_one = ('User',)


class Game(Model):
    has_many = ('State', 'User',)


if __name__ == '__main__':
    import rethinkdb as r
    import logging
    from remodel.helpers import create_tables, create_indexes
    from remodel.registry import index_registry

    logging.basicConfig(level=logging.INFO)
    with pool.get() as conn:
        logging.info("Drop old db")
        try:
            r.db_drop('game').run(conn)
        except:
            pass
        logging.info("Create db")
        r.db_create('game').run(conn)

    logging.info("Create tables")
    create_tables()
    logging.info("Register secondary indices")
    index_registry.register("User", "username")
    logging.info("Create indices")
    create_indexes()

    logging.info("Load initial data")
    Piece.factory('Headquarters', 0., ['https://commons.wikimedia.org/wiki/File:NATO_Map_Symbol_-_Headquarters_Unit.svg#/media/File:NATO_Map_Symbol_-_Headquarters_Unit.svg'])
    Piece.factory('Light Infantry', 10., ['https://commons.wikimedia.org/wiki/File:NATO_Map_Symbol_-_Infantry_(Light).svg#/media/File:NATO_Map_Symbol_-_Infantry_(Light).svg'])
    Piece.factory('Mounted Infantry', 30., ['https://commons.wikimedia.org/wiki/File:NATO_Map_Symbol_-_Mounted_Infantry.svg#/media/File:NATO_Map_Symbol_-_Mounted_Infantry.svg'])
    User.factory('admin', roles=["admin"])
