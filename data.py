#!/usr/bin/env python

import logging
import operator
import functools
import time
import extlibs.peewee as peeewee

import models
import product
import settings


class Access:

    def __init__(self):
        models.db.connect()
        models.db.create_tables([models.User, product.Product], True)

    def get_user_by_properties(self, parameters):
        clauses = []
        for k, v in parameters.items():
            if v.startswith(">"):
                clauses.append((getattr(product.Product, k) > v.lstrip(">=")))
            elif v.startswith("<"):
                clauses.append((getattr(product.Product, k) <= v.lstrip("<=")))
            else:
                clauses.append((getattr(product.Product, k) == v.lstrip("=")))
        # Find the products which match the requirements and return the
        # corresponding user that the product is linked to (Foreign Key)
        # Make sure the user is marked as dirty since its data will probably
        # not be true within a few minutes.
        try:
            q = product.Product.select().where(functools.reduce(operator.and_, clauses))
            user = q.join(models.User).where(models.User.dirty == False).get().user
            user.dirty = True
            user.save()
            return user.cip
        except peewee.DoesNotExist:
            return ''

    def get_dirty_users(self):
        delta = time.time() - settings.dirty_user_refresh
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
