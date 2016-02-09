#!/usr/bin/env python

import logging
import os
import extlibs.peewee as orm

import settings

db = orm.SqliteDatabase(os.path.join(os.path.dirname(os.path.realpath(__file__)), settings.db_name), pragmas=(("busy_timeout", "30000"),))
#db = orm.PostgresqlDatabase(settings.db_name, user='postgres', port=5432)

class BaseModel(orm.Model):
    class Meta:
        database = db

class User(BaseModel):
    personId = orm.BigIntegerField(primary_key=True)
    dirty = orm.BooleanField(default=True)
    lastUpdate = orm.DateTimeField(null=True)
