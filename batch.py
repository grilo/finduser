#!/usr/bin/env python

import logging
logging.basicConfig(format='%(asctime)s::%(levelname)s::%(message)s')
import argparse
import sys
import time

import finduser.finduser
import finduser.data
import settings


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Execute a command line utility, parse its output and insert it into a database.')

    parser.add_argument("-v", "--verbose", action="store_true", \
        help="Increase output verbosity")
    parser.add_argument("-w", "--workers", type=int, default=settings.batch_default_workers, \
        help="Amount of subprocesses to launch which will execute the script")
    parser.add_argument("-x", "--execute", default=settings.batch_find_user_exec, \
        help="The utility to be executed (fixed parameters may be specified).")

    args = parser.parse_args()

    logging.getLogger().setLevel(logging.INFO)
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    f = finduser.finduser.FindUser(args.execute, args.workers, settings.default_encoding)
    dao = finduser.data.Access(settings.db_default_properties, settings.db_dirty_user_refresh)

    while True:
        # Get the list of dirty users which represent users with tainted
        # or outdated info, and freshen their data by querying GTM directly
        for products in f.parallel_find(dao.get_dirty_users()):
            dao.update_products(products)

        logging.info("All users processed, taking a nap...")
        time.sleep(5)
