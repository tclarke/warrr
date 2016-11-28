#!/usr/bin/env python
from remodel.models import Model
from remodel.connection import pool

pool.configure(db='game')


class Piece(Model):
    belongs_to = ('State',)

    @staticmethod
    def factory(name, dist, image_urls):
        Piece.create(name=name, dist=dist, image_urls=image_urls).save()


class User(Model):
    belongs_to = ('State', 'Game')


class State(Model):
    belongs_to = ('Game',)
    has_many = ('Piece',)
    has_one = ('User',)


class Game(Model):
    has_many = ('State', 'User',)


if __name__ == '__main__':
    import rethinkdb as r
    from remodel.helpers import create_tables, create_indexes
    with pool.get() as conn:
        try:
            r.db_drop('game').run(conn)
        except:
            pass
        r.db_create('game').run(conn)

    create_tables()
    create_indexes()

    Piece.factory('Headquarters', 0., ['https://commons.wikimedia.org/wiki/File:NATO_Map_Symbol_-_Headquarters_Unit.svg#/media/File:NATO_Map_Symbol_-_Headquarters_Unit.svg'])
    Piece.factory('Light Infantry', 10., ['https://commons.wikimedia.org/wiki/File:NATO_Map_Symbol_-_Infantry_(Light).svg#/media/File:NATO_Map_Symbol_-_Infantry_(Light).svg'])
    Piece.factory('Mounted Infantry', 30., ['https://commons.wikimedia.org/wiki/File:NATO_Map_Symbol_-_Mounted_Infantry.svg#/media/File:NATO_Map_Symbol_-_Mounted_Infantry.svg'])
