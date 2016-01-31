#!/usr/bin/env python

import logging
import subprocess
import shlex
import json
import multiprocessing
import time

import settings


class FindUser:
    def __init__(self, command='./script.sh', workers=multiprocessing.cpu_count() ** 2):
        self.command = command
        self.workers = workers

    def _openDate_to_epoch(self, ts):
        # Also normalize the data being sent which always uniform
        if "dayOfMonth" in ts.keys():
            ts["day"] = ts["dayOfMonth"]
        if "hourOfDay" in ts.keys():
            ts["hour"] = ts["hourOfDay"]
        if "second" not in ts.keys():
            ts["second"] = "00"
        struct_time = time.strptime(" ".join([ts["year"], ts["month"], ts["day"], \
                        ts["hour"], ts["minute"], ts["second"]]), "%Y %m %d %H %M %S")
        return time.mktime(struct_time)

    def find(self, uuid):
        logging.warn("Querying for user %d" % (uuid))
        cmd = " ".join([self.command, str(uuid)])
        stdout = subprocess.check_output(shlex.split(cmd), stderr= subprocess.STDOUT)

        products = []
        for d in json.loads(stdout.decode(settings.default_encoding)):
            d["user"] = uuid
            d["openDate"] = self._openDate_to_epoch(d["openDate"])
            products.append(d)
        return products

    def parallel_find(self, iterator):
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
