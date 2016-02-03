#!/usr/bin/env python

import logging
import operator
import functools
import time
import extlibs.peewee as orm

import models
import settings
import schema

class DoesNotExist(orm.DoesNotExist):
    pass


class Access:

    def __init__(self):
        self.product_validator = schema.Validator(models.Product.python_schema())
        models.db.connect()
        models.db.create_tables([models.User, models.Product], True)

    def get_product_fields(self):
        return models.Product.python_schema()

    def get_user_by_properties(self, properties):
        logging.debug("Get user by properties: %s" % (properties))
        assert type(properties) == dict

        # Set default parameters
        for p in properties["product"]:
            if not self.product_validator.partial(p):
                raise AssertionError
            for k, v in settings.db_default_properties.items():
                if k in p.keys(): continue
                p[k] = v

        # For this to work, we need to create an intersection between
        # all products. Meaning, get the users which match product1,
        # product2, product3, ..., and then intersect the results,
        # fetching the first user which matches all of the queries
        lists_of_users = []
        for p in properties["product"]:
            clauses = []
            for k, v in p.items():
                if type(v) == bool:
                    clauses.append((getattr(models.Product, k) == v))
                elif v.startswith(">"):
                    clauses.append((getattr(models.Product, k) > v.lstrip(">=")))
                elif v.startswith("<"):
                    clauses.append((getattr(models.Product, k) <= v.lstrip("<=")))
                else:
                    clauses.append((getattr(models.Product, k) == v.lstrip("=")))
            query = models.User.select().where(models.User.dirty == False).join(models.Product).where(functools.reduce(operator.and_, clauses))
            lists_of_users.append(query)

        """
        Of interest is noting that the '&' operator has different context:
        in WHERE clauses it works like AND
        If the left and right side are already built SQL queries, it works
        as INTERSECT


        From peewee (orm) documentation:

        customers = Customer.select(Customer.city).where(Customer.state == 'KS')
        stores = Store.select(Store.city).where(Store.state == 'KS')

        # Get all cities in kanasas where we have both customers and stores.
        cities = (customers & stores).order_by(SQL('city'))
        """

        try:
            user = functools.reduce(operator.and_, lists_of_users).get()
            user.dirty = True
            user.save()
            return user.cip
        except orm.DoesNotExist:
            raise LookupError

    def get_dirty_users(self):
        delta = time.time() - settings.db_dirty_user_refresh
        return [u.cip for u in models.User.select(models.User.cip).where(models.User.dirty == True).where(models.User.lastUpdate < delta).limit(10000)]

    def update_products(self, products):
        if len(products) <= 0: return

        # Ensure that the data is actually good for insertion
        validated = []
        for p in products:
            if self.product_validator.full(p):
                validated.append(p)
            else:
                logging.error("Ignoring invalid data (%s): %s" % (p["user"], p))

        if len(validated) <= 0:
            logging.error("No valid entries found for the user found, refusing any updates.")

        logging.warning("Inserting products for: %s" % (str(products[0]["user"])))
        with models.db.atomic():
            q = models.Product.insert_many(validated).upsert(upsert=True)
            q.execute()

        # Mark the user's data as fresh
        return models.User.update(dirty=False, lastUpdate=time.time()).where(models.User.cip == products[0]["user"]).execute()


    def touch_user(self, properties):
        with models.db.atomic():
            models.User.insert(**properties).upsert(upsert=True).execute()
