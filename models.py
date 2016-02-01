import logging
import extlibs.peewee as orm

import settings

db = orm.SqliteDatabase(settings.db_name, pragmas=(
        ("busy_timeout", "30000"),
    )
)

class BaseModel(orm.Model):
    class Meta:
        database = db

class User(BaseModel):
    cip = orm.BigIntegerField(primary_key=True)
    dirty = orm.BooleanField(default=True)
    lastUpdate = orm.DateTimeField(null=True)
