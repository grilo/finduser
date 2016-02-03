#!/usr/bin/env python

import logging
import subprocess
import shlex
import json
import multiprocessing
import time

import settings


class FindUser:
    def __init__(self, command, workers=multiprocessing.cpu_count() ** 2):
        self.command = command
        self.workers = workers

    def _openDate_to_epoch(self, ts):
        """Convert a dict representing a date into Epoch.

        Because RDBMS don't like hierarchical data.

        Args:
            ts (dict): The date in a whatever format.

        Returns:
            float: The epoch for that date.

        """
        # Also normalize the data being sent which always uniform
        for k, v in ts.items():
            ts[k] = str(v)
            if k == "dayOfMonth":
                ts["day"] = ts[k]
            elif k == "hourOfDay":
                ts["hour"] = ts[k]

        if "second" not in ts.keys():
            ts["second"] = "00"

        time_string = " ".join([ts["year"], ts["month"],  ts["day"], \
                                ts["hour"], ts["minute"], ts["second"]])
        return time.mktime(time.strptime(time_string, "%Y %m %d %H %M %S"))

    def find(self, uuid):
        """Execute a CLI utility and return the results.

        This is the meat of the find user. Since Python has much poorer drivers
        for esoteric stuff than Java, we simply created a very small CLI util
        which does the work for us and use Python to glue everything together.

        Args:
            uuid (str): A parameter passed to the CLI util (self.command).

        Returns:
            list(dict): The [somewhat altered] JSON output of the utility.
        """
        logging.warn("Querying for user %d" % (uuid))
        cmd = " ".join([self.command, str(uuid)])

        try:
            stdout = subprocess.check_output(shlex.split(cmd), stderr= subprocess.STDOUT)
        except subprocess.CalledProcessError:
            logging.error("User doesn't seem to exist: %s" % (uuid))
            return []

        products = []
        for d in json.loads(stdout.decode(settings.default_encoding)):
            d["user"] = uuid
            if not "openDate" in d.keys():
                logging.error("The user information seems incorrect: %s" % (d))
                return []
            d["openDate"] = self._openDate_to_epoch(d["openDate"])
            products.append(d)
        return products

    def parallel_find(self, iterator):
        """In yer face GIL!"""
        proc_pool = multiprocessing.Pool(self.workers)
        for i in proc_pool.imap_unordered(self.find, iterator):
            yield i
        proc_pool.close()
        proc_pool.join()


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    f = FindUser("python simulate.py")
    #import pprint
    #pprint.pprint(f.find(4))
    #[x for x in f.parallel_find(range(100))]
