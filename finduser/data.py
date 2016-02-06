#!/usr/bin/env python

import logging
import operator
import functools
import time
import re

import extlibs.peewee as orm

import finduser.models


class Access:

    def __init__(self, default_properties, dirty_user_refresh):
        logging.info("Data Access Object initialized.")
        self.default_properties = default_properties
        self.dirty_user_refresh = dirty_user_refresh
        self.dynamic_models = {}
        finduser.models.db.connect()
        finduser.models.db.create_tables([finduser.models.User], True)

    def generate_model(self, table, properties):
        logging.info("Generating model for (%s)." % (table))
        class DynamicTable(finduser.models.BaseModel):
            user = orm.ForeignKeyField(finduser.models.User, related_name=table)

        for k, v in properties.items():
            orm_field = None
            if v == 'bool':
                orm_field = 'Boolean'
            elif v == 'date':
                orm_field = 'DateTime'
            elif v == 'str':
                orm_field = 'Char'
            elif v == 'float':
                orm_field = 'Double'
            elif v == 'int':
                orm_field = 'Integer'
            else:
                logging.error("Unknown field type (%s). Unable to create model for table (%s)." % (v, table))
                raise AttributeError

            field = getattr(orm, orm_field + 'Field')
            field().add_to_class(DynamicTable, k)

        finduser.models.db.create_tables([DynamicTable], True)
        self.dynamic_models[table] = DynamicTable

    def _get_table_model(self, table):
        return self.dynamic_models[table]

    def _dbIO(self, query):
        """Database IO isolation."""
        logging.debug("DBIO: %s" % query)
        try:
            return query.execute()
        except orm.OperationalError:
            logging.critical("Unable to perform database update, probably due to locking: %s" % (query))
            raise IOError

    def _split_operator_value(self, expression):
        """Parse a string, return a tuple of (operator, value)."""
        op, new_value = '', str(expression)

        # We have no match, this means there's no operator attached
        m = re.search('([<=>]+)(.*)', new_value)
        if not m is None:
            op, new_value = m.group(1), m.group(2)
        # bool(str) doesn't work
        if new_value == "True":
            return '', True
        elif new_value == "False":
            return '', False
        else:
            return op, new_value

    def get_dirty_users(self):
        """Returns a list of personIds that have tainted data (used by test cases)."""
        logging.info("Scanning for dirty users.")
        delta = time.time() - self.dirty_user_refresh
        query = finduser.models.User.select(finduser.models.User.personId) \
                    .where(finduser.models.User.dirty == True) \
                    .where(finduser.models.User.lastUpdate < delta) \
                    .limit(10000)
        return [u.personId for u in query]

    def refresh_user(self, personId, lastUpdate=0.0):
        """Mark a user to be refreshed, lastUpdate will control exactly when."""
        logging.info("Requesting user refresh: %s" % personId)
        properties = {"personId": personId, "dirty": True, "lastUpdate": lastUpdate}

        with finduser.models.db.atomic():
            self._dbIO(finduser.models.User.insert(**properties).upsert(upsert=True))

    def build_query(self, table, raw_properties):
        """Generate a query which matches the users for this given product.

        We also inject any default values if the user hasn't overriden them,
        and actually validate the data before sending it down the pipe. We
        take special care with the information we recieve since it still
        contains the operators (as it should, otherwise we don't know how to
        build an actual query).

        Args:
            table (str): The table to look for (product, movements, etc.)
            raw_properties (dict): { accBalance: >=0, accBlocked: =1, ...}
                Note: boolean values withouth an operator are also supported

        Returns:
            ORM query (peewee.Query)
        """
        clauses = []
        properties = raw_properties.copy()

        # Defaults
        for k, v in self.default_properties[table].items():
            if not k in properties.keys():
                properties[k] = v

        # Validate and build query
        for k, v in properties.items():
            try:
                op, v = self._split_operator_value(v)
            except TypeError:
                logging.critical("Unable to split operator and value for: %s" % (v))
                raise TypeError

            if op.startswith(">"):
                clauses.append((getattr(self._get_table_model(table), k) >= v))
            elif op.startswith("<"):
                clauses.append((getattr(self._get_table_model(table), k) <= v))
            else:
                clauses.append((getattr(self._get_table_model(table), k) == v))

        q = finduser.models.User.select() \
            .where(finduser.models.User.dirty == False) \
            .join(self._get_table_model(table)) \
            .where(functools.reduce(operator.and_, clauses))
        return q



    def update(self, personId, results):
        """Update the personId's products (or movements, or something else).

        This is usually invoked as soon as the GTM.Finder process collects the data.

        Args:
            personId (string)
            products (list<dict>): { accBlocked: True, accBalance: 0, ... }

        Returns:
            (int) The number of rows updated
        """
        for table, values in results.items():

            if len(values) <= 0: continue

            with finduser.models.db.atomic():
                logging.warning("Inserting (%s) (%d) for: %s" % (table, len(values), personId))
                q = self._get_table_model(table).insert_many(values).upsert(upsert=True)
                self._dbIO(q)

        # Mark the user's data as fresh
        return self._dbIO(finduser.models.User.update(dirty=False, lastUpdate=time.time()) \
                    .where(finduser.models.User.personId== personId))


    def get_user_by_properties(self, properties):
        """Get a user which matches ALL properties (AND clauses).

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

        Args:
            properties (dict<list<dict>>) { accBlocked: True, accBalance: 0, ... }
                The first dict contains the type of item we're looking for
                (product, movements, etc.), and then it has a list of dicts. This
                second dict contains the properties of that specific product we're
                looking for. This will allow us to answer queries such as "give me
                a user which has two accounts of type X, 5 international transfers
                and a broker account.

        Returns:
            personId
        """
        logging.info("Get user by properties: %s" % (properties))
        assert type(properties) == dict

        lists_of_users = []
        for table, values in properties.items():
            for val in values:
                lists_of_users.append(self.build_query(table, val))

        try:
            user = self._dbIO(functools.reduce(operator.and_, lists_of_users).limit(1)).next()
        except orm.DoesNotExist:
            logging.warning("Unable to find any personId matching the criteria.")
            raise LookupError
        except StopIteration:
            logging.warning("Unable to find any personId matching the criteria.")
            raise LookupError
        logging.info("Found user: %s" % (user.personId))
        self.refresh_user(user.personId, time.time())
        return user.personId
