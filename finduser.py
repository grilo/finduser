#!/usr/bin/env python

import logging
import subprocess
import shlex
import json
import multiprocessing


class FindUser:
    def __init__(self, command='./script.sh', workers=multiprocessing.cpu_count() ** 2):
        self.command = command
        self.workers = workers

    def find(self, uuid):
        logging.debug("Querying for user %d" % (uuid))
        cmd = " ".join([self.command, str(uuid)])
        stdout = subprocess.check_output(shlex.split(cmd), stderr= subprocess.STDOUT)
        data = json.loads(stdout.decode('utf8'))
        return {
            "cip": uuid,
            "products": data,
        }

    def parallel_find(self, iterator):
        proc_pool = multiprocessing.Pool(self.workers)
        return proc_pool.imap_unordered(self.find, iterator)

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    f = FindUser("python simulate.py")
    #print(f.find(1))
    [x for x in f.parallel_find(range(100))]
