import logging
import peewee

import models
import product


class Access:

    def __init__(self):
        models.db.connect()
        models.db.create_tables([models.User, product.Product], True)

    """
        Transform the map of property_one: value_one, property_two: value_two
        into a query of property_one = value_one AND property_two = value_two
    """
    def _dict_to_query(self, table, parameters):
        sql = "SELECT * FROM %s WHERE " % (table)
        query = []
        for k, v in parameters.items():
            try:
                getattr(models.User, k)
                query.append("%s = %s" % (k, v))
            except AttributeError:
                return []
        return sql + " AND ".join(query)


    def get_user_by_properties(self, parameters, limit=1):
        sql = self._dict_to_query(models.User._meta.db_table, parameters)
        if limit > 0:
            sql += " LIMIT 1;"
        logging.debug(sql)

        rq = peewee.RawQuery(models.User, sql)
        for user in rq.execute():
            # Every time we return a user, mark it as dirty in the database,
            # helping us keeping the user data fresh after its used
            user.dirty = True
            user.save()
            yield user

    def get_dirty_users(self):
        return [u.cip for u in models.User.select(models.User.cip).where(models.User.dirty == True).limit(10000)]

    def insert_data(self, products):
        logging.warn("Inserting products for: %s" % (str(products[0]["user"])))
        with models.db.atomic():
            product.Product.insert_many(products).upsert(upsert=True).execute()
            #product.Product.insert_many(products).execute()

        return models.User.update(dirty=False).where(models.User.cip == products[0]["user"]).execute()


    def touch_user(self, properties):
        try:
            with models.db.atomic():
                u = models.User.get(models.User.cip == properties["cip"])
                u.dirty = True
                return u.save()
        except peewee.DoesNotExist:
            with models.db.atomic():
                return models.User.create(**properties)
