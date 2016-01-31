import logging
import peewee
import pprint

import settings

db = peewee.SqliteDatabase(settings.db_name, pragmas=(
        ("busy_timeout", "30000"),
    )
)

class BaseModel(peewee.Model):
    class Meta:
        database = db

class User(BaseModel):
    cip = peewee.BigIntegerField(primary_key=True)
    dirty = peewee.BooleanField(default=True)
    lastUpdate = peewee.DateTimeField(null=True)
