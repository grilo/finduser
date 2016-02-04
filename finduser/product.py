#!/usr/bin/env python

import logging
import subprocess
import shlex
import json
import multiprocessing
import time


class GTM:
    def __init__(self, command, workers=multiprocessing.cpu_count() ** 2, encoding='utf8'):
        self.command = command
        self.workers = workers
        self.encoding = encoding

    def normalize_json(self, personId, p):
        product = p.copy()
        product["user"] = personId

        if not "openDate" in product.keys():
            # Set the date for the original epoch
            timestamp = "1970 01 01 00 00 00"
        else:
            date = product["openDate"]
            # Normalize the date from 'wtf' to 'epoch'
            if "dayOfMonth" in date.keys():
                date["day"] = date.pop("dayOfMonth")
            if "hourOfDay" in date.keys():
                date["day"] = date.pop("hourOfDay")
            if not "second" in date.keys():
                date["second"] = "0"
            date["month"] = str(int(date["month"]) + 1)

            for k, v in date.items():
                date[k] = str(v)
            timestamp = " ".join([
                            date["year"], date["month"], date["day"],
                            date["hour"], date["minute"], date["second"],
                        ])

        product["openDate"] = time.mktime(time.strptime(timestamp, "%Y %m %d %H %M %S"))
        return product

    def find(self, personId):
        """Execute a CLI utility and return the results.

        This is the meat of the find user. Since Python has much poorer drivers
        for esoteric stuff than Java, we simply created a very small CLI util
        which does the work for us and use Python to glue everything together.

        Args:
            personId (str): A parameter passed to the CLI util (self.command).

        Returns:
            list(dict): The [somewhat altered] JSON output of the utility.
        """
        logging.warn("Querying for user %d" % (personId))
        cmd = " ".join([self.command, str(personId)])

        try:
            raw_products = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            logging.error("User doesn't seem to exist: %s" % (personId))
            return []

        product_list = []
        for p in json.loads(raw_products.decode(self.encoding)):
            product_list.append(self.normalize_json(personId, p))
        return (personId, product_list)

    def parallel_find(self, iterator):
        """In yer face GIL!"""
        proc_pool = multiprocessing.Pool(self.workers)
        for i in proc_pool.imap_unordered(self.find, iterator):
            yield i
        proc_pool.close()
        proc_pool.join()
