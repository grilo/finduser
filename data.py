#!/usr/bin/env python

import logging
import operator
import functools
import time
import extlibs.peewee as orm

import models
import product
import settings


class Access:

    def __init__(self):
        models.db.connect()
        models.db.create_tables([models.User, product.Product], True)

    def get_product_fields(self):
        return product.get_schema()

    def get_user_by_properties(self, properties):
        logging.debug("Get user by properties: %s" % (properties))

        # Set default parameters
        for p in properties["product"]:
            for k, v in settings.db_default_properties.items():
                if k in p.keys(): continue
                p[k] = v

        # For this to work, we need to create an intersection between
        # all products. Meaning, get the users which match product1,
        # product2, product3, ..., and then intersect the results,
        # fetching the first user which matches all of the queries
        lists_of_users = []
        for p in properties["product"]:
            print(p)
            clauses = []
            for k, v in p.items():
                if v.startswith(">"):
                    clauses.append((getattr(product.Product, k) > v.lstrip(">=")))
                elif v.startswith("<"):
                    clauses.append((getattr(product.Product, k) <= v.lstrip("<=")))
                else:
                    clauses.append((getattr(product.Product, k) == v.lstrip("=")))
            query = models.User.select().where(models.User.dirty == False).join(product.Product).where(functools.reduce(operator.and_, clauses))
            lists_of_users.append(query)

        """
        From peewee (orm) documentation:

        customers = Customer.select(Customer.city).where(Customer.state == 'KS')
        stores = Store.select(Store.city).where(Store.state == 'KS')

        # Get all cities in kanasas where we have both customers and stores.
        cities = (customers & stores).order_by(SQL('city'))
        """

        # Of interest is noting that the '&' operator has different context:
        # in WHERE clauses it works like AND
        # If the left and right side are already built SQL queries, it works
        # as INTERSECT

        try:
            user = functools.reduce(operator.and_, lists_of_users).get()
            user.dirty = True
            user.save()
            logging.info("Found user for query: %s" % (properties))
            return user.cip
        except orm.DoesNotExist:
            logging.error("No user found for query: %s" % (properties))
            return ''

    def get_dirty_users(self):
        delta = time.time() - settings.db_dirty_user_refresh
        return [u.cip for u in models.User.select(models.User.cip).where(models.User.dirty == True).where(models.User.lastUpdate < delta).limit(10000)]

    def update_products(self, products):
        if len(products) <= 0: return

        # Ensure that the data is actually good for insertion
        validated = []
        for p in products:
            if not product.validate(p):
                logging.error("Ignoring invalid data (%s): %s" % (p["user"], p))
                continue
            validated.append(p)

        logging.warning("Inserting products for: %s" % (str(products[0]["user"])))
        with models.db.atomic():
            product.Product.insert_many(validated).upsert(upsert=True).execute()

        # Mark the user's data as fresh
        return models.User.update(dirty=False, lastUpdate=time.time()).where(models.User.cip == products[0]["user"]).execute()


    def touch_user(self, properties):
        with models.db.atomic():
            models.User.insert(**properties).upsert(upsert=True).execute()
