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

class Product(BaseModel):
    user = peewee.ForeignKeyField(User, related_name='products')
    cuentanaranja = peewee.BigIntegerField(null=True)
    cuentanaranjabalance = peewee.BigIntegerField(null=True)
    cuentanomina = peewee.BigIntegerField(null=True)
    cuentanominabalance = peewee.BigIntegerField(null=True)


class DAO:

    def __init__(self):
        db.connect()
        db.create_tables([User], True)

    """
        Transform the map of property_one: value_one, property_two: value_two
        into a query of property_one = value_one AND property_two = value_two
    """
    def _dict_to_query(self, table, parameters):
        sql = "SELECT * FROM %s WHERE " % (table)
        query = []
        for k, v in parameters.items():
            try:
                getattr(User, k)
                query.append("%s = %s" % (k, v))
            except AttributeError:
                return []
        return sql + " AND ".join(query)


    def get_user_by_properties(self, parameters, limit=1):
        sql = self._dict_to_query(User._meta.db_table, parameters)
        if limit > 0:
            sql += " LIMIT 1;"
        logging.debug(sql)

        rq = peewee.RawQuery(User, sql)
        for user in rq.execute():
            # Every time we return a user, mark it as dirty in the database,
            # helping us keeping the user data fresh after its used
            user.dirty = True
            user.save()
            yield user

    def get_dirty_users(self):
        for u in User.select(User.cip).where(User.dirty == True):
            yield u.cip

    def update_user(self, props):
        props["dirty"] = 0
        with db.atomic():
            return User.update(**props).where(User.cip == props["cip"]).execute()

    def touch_user(self, properties):
        try:
            with db.atomic():
                u = User.get(User.cip == properties["cip"])
                u.dirty = True
                return u.save()
        except peewee.DoesNotExist:
            with db.atomic():
                return User.create(**properties)
