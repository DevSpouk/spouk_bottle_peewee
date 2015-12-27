#!/usr/local/bin/python
__author__ = 'spouk'

__all__ = ['Database', 'DatabaseMiddleware']

import peewee
from peewee import *
import sys


class ImproperlyConfigured(Exception):
    pass


class Database(object):
    """peewee database support for bottle"""

    database_types = dict(
        mysql='mysql',
        psql='psql',
        sqlute='sqplite',
    )

    def __init__(self, database_config, type_database='psql'):
        self.type_database = type_database
        assert self.type_database in self.database_types, "Wrong database type"
        self.database_config = database_config
        self.app = None
        self.initdatabase()
        self.Model = self.get_model_class()

    def load_class(self, s):
        path, klass = s.rsplit('.', 1)
        __import__(path)
        mod = sys.modules[path]
        return getattr(mod, klass)

    def initdatabase(self):
        try:
            self.dbname = self.database_config.pop('name')
            self.db_engine = self.database_config.pop('engine')
        except KeyError:
            raise ImproperlyConfigured('Please specify a "name" and "engine" for your database')
        try:
            self.database_class = self.load_class(self.db_engine)
            assert issubclass(self.database_class, peewee.Database)
        except ImportError:
            raise ImproperlyConfigured('Unable to import: "%s"' % self.db_engine)
        except AttributeError:
            raise ImproperlyConfigured('Database engine not found: "%s"' % self.db_engine)
        except AssertionError:
            raise ImproperlyConfigured('Database engine not a subclass of peewee.Database: "%s"' % self.db_engine)

        self.database = self.database_class(self.dbname, **self.database_config)

    def get_model_class(self):
        class BaseModel(Model):
            class Meta:
                database = self.database

        return BaseModel

    def connect_db(self):
        self.database.connect()

    def close_db(self):
        if not self.database.is_closed():
            self.database.close()


class DatabaseMiddleware(object):
    """peewee middleware for bottle, support for database"""
    database_types = dict(
        mysql='mysql',
        psql='psql',
        sqlute='sqplite',
    )

    def __init__(self, app, db, type_database='psql'):
        self.app = app
        self.type_database = type_database
        assert self.type_database in self.database_types, "Wrong database type"
        self.db = db

    def __call__(self, environ, start_response):
        environ['db'] = self
        self.app.db = self.db

        if self.type_database == 'mysql':
            self.app.add_hook('before_request', self.connect_db)
            self.app.add_hook('after_request', self.close_db)

        if self.type_database == 'psql':
            self.app.db_status = False
            self.app.add_hook('before_request', self.psql_check_connector)

        return self.app.wsgi(environ, start_response)

    def psql_check_connector(self):
        if self.db.is_closed():
            self.db.connect()
            self.app.db_status = True
            print("[PSQL DB] database connected success")
        else:
            print("[PSQL DB] database already have open connector")

    def connect_db(self):
        self.db.connect()

    def close_db(self):
        if not self.db.is_closed():
            self.db.close()


