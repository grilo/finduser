#!/usr/bin/env python

import logging
logging.basicConfig(format='%(asctime)s::%(levelname)s::%(message)s')
import argparse
import sys
import time

import finduser
import data


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Execute a command line utility, parse its output and insert it into a database.')

    parser.add_argument("-v", "--verbose", action="store_true", \
        help="Increase output verbosity")
    parser.add_argument("-w", "--workers", type=int, default=4, \
        help="Amount of subprocesses to launch which will execute the script")
    parser.add_argument("-x", "--execute", default='./script.sh', \
        help="The utility to be executed (fixed parameters may be specified).")

    args = parser.parse_args()

    logging.getLogger().setLevel(logging.INFO)
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    f = finduser.FindUser("python simulate.py", args.workers)
    dao = data.Access()

    while True:
        # Get the list of dirty users which represent users with tainted
        # or outdated info, and freshen their data by querying GTM directly
        for products in f.parallel_find(dao.get_dirty_users()):
            dao.update_products(products)

        logging.info("All users processed, taking a nap...")
        time.sleep(5)
