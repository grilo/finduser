import logging
import peewee

db = peewee.SqliteDatabase('users.sqlite')

class BaseModel(peewee.Model):
    class Meta:
        database = db

class User(BaseModel):
    cip = peewee.BigIntegerField(primary_key=True)
    cuentanaranja = peewee.BigIntegerField()
    cuentanaranjabalance = peewee.BigIntegerField()
    cuentanomina = peewee.BigIntegerField()
    cuentanominabalance = peewee.BigIntegerField()

db.connect()
db.create_tables([User], True)

def getquery(parameters):
    sql = "SELECT * FROM %s WHERE " % (User._meta.db_table)
    query = []
    for k, v in parameters.items():
        try:
            getattr(User, k)
            query.append("%s = %s" % (k, v))
        except AttributeError:
            return False

    if query:
        sql += " %s" % " AND ".join(query) + " LIMIT 1;"

    logging.debug(sql)
    rq = peewee.RawQuery(User, sql)
    for obj in rq.execute():
        return obj._data
