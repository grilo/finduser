#!/usr/bin/env python

import logging
import operator
import functools
import time
import re

import extlibs.peewee as orm

import finduser.models
import finduser.schema


class Access:

    def __init__(self, default_properties, dirty_user_refresh):
        self.default_properties = default_properties
        self.dirty_user_refresh = dirty_user_refresh
        self.product_validator = finduser.schema.Validator(finduser.models.Product.python_schema())
        finduser.models.db.connect()
        finduser.models.db.create_tables([finduser.models.User, finduser.models.Product], True)

    def _dbIO(self, query):
        try:
            return query.execute()
        except peewee.OperationalError:
            logging.critical("Unable to perform database update, probably due to locking: %s" % (query))
            raise IOError

    def _split_operator_value(self, expression):
        # Don't do weird stuff for booleans
        if type(expression) == bool:
            return '', expression

        # We have no match, this means there's no operator attached
        m = re.search('([<=>]+)(.*)', expression)
        if m is None:
            return '', expression
        return m.group(1), m.group(2)

    def get_product_fields(self):
        return finduser.models.Product.python_schema()

    def get_product_query(self, raw_product):
        clauses = []
        product = raw_product.copy()

        # Set default values
        for k, v in self.default_properties["product"].items():
            if not k in product.keys():
                product[k] = v

        for k, v in product.items():
            try:
                op, v = self._split_operator_value(v)
            except TypeError:
                logging.critical("Unable to split operator and value for: %s" % (v))
                raise TypeError

            if not self.product_validator.partial({k: v}):
                raise AssertionError

            if op.startswith(">"):
                clauses.append((getattr(finduser.models.Product, k) >= v))
            elif op.startswith("<"):
                clauses.append((getattr(finduser.models.Product, k) <= v))
            else:
                clauses.append((getattr(finduser.models.Product, k) == v))

        return finduser.models.User.select() \
                .where(finduser.models.User.dirty == False) \
                .join(finduser.models.Product) \
                .where(functools.reduce(operator.and_, clauses))


    def get_user_by_properties(self, properties):
        logging.debug("Get user by properties: %s" % (properties))
        assert type(properties) == dict

        lists_of_users = []
        for product in properties["product"]:
            lists_of_users.append(self.get_product_query(product))

        """
        For this to work, we need to create an intersection between
        all products. Meaning, get the users which match product1,
        product2, product3, ..., and then intersect the results,
        fetching the first user which matches all of the queries

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
            user = self._dbIO(functools.reduce(operator.and_, lists_of_users).limit(1)).next()
            self.refresh_user(user.personId, time.time())
            return user.personId
        except orm.DoesNotExist:
            raise LookupError

    def get_dirty_users(self):
        delta = time.time() - self.dirty_user_refresh
        query = finduser.models.User.select(finduser.models.User.personId) \
                    .where(finduser.models.User.dirty == True) \
                    .where(finduser.models.User.lastUpdate < delta) \
                    .limit(10000)
        return [u.personId for u in query]

    def update_products(self, personId, products):
        if len(products) <= 0:
            # Either the user doesn't exist or it has no products,
            # we mark it as fresh and return
            return self._dbIO(finduser.models.User.update(dirty=False, lastUpdate=time.time()) \
                        .where(finduser.models.User.personId == personId))

        # Ensure that the data is actually good for insertion
        valid_products = [p for p in products if self.product_validator.full(p)]
        if len(valid_products) <= 0:
            logging.error("No valid entries found for personId (%s), refusing updates." % (personId))
            return

        with finduser.models.db.atomic():
            logging.warning("Inserting products for: %s" % (personId))
            q = finduser.models.Product.insert_many(valid_products).upsert(upsert=True)
            self._dbIO(q)

        # Mark the user's data as fresh
        return self._dbIO(finduser.models.User.update(dirty=False, lastUpdate=time.time()) \
                    .where(finduser.models.User.personId== personId))


    def refresh_user(self, personId, lastUpdate=0.0):
        properties = {"personId": personId, "dirty": True, "lastUpdate": lastUpdate}

        with finduser.models.db.atomic():
            self._dbIO(finduser.models.User.insert(**properties).upsert(upsert=True))
