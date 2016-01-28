#!/usr/bin/env python

import logging
import argparse
import sys
import time
import pprint

import task
import finduser
import models



def bulk_insert(gtm_users):
    if not gtm_users: return

    fields = ['cip', 'cuentanaranja', 'cuentanaranjabalance', 'cuentanomina', 'cuentanominabalance']
    big_list = []
    # Create a key:value hash required by peewee for insertion
    for u in gtm_users:
        big_list.append(dict(zip(fields, u.strip().split("|"))))

    with models.db.atomic():
        logging.info("Bulk insert of %s" % (pprint.pformat(big_list)))
        models.User.insert_many(big_list)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Execute a command line utility, parse its output and insert it into a database. Also launches a small web service which allows querying the data.')

    parser.add_argument("-v", "--verbose", action="store_true", \
        help="Increase output verbosity")
    parser.add_argument("-w", "--workers", type=int, default=4, \
        help="Amount of subprocesses to launch which will execute the script")
    parser.add_argument("-f", "--file", \
        help="The file which will read parameters to pass to the utility.")
    parser.add_argument("-s", "--start", type=int, default=0, \
        help="Ignore the first X entries.")
    parser.add_argument("-x", "--execute", default='./script.sh', \
        help="The utility to be executed (fixed parameters may be specified).")

    args = parser.parse_args()

    if args.file is None:
        logging.critical("The option --file <filename> is mandatory.")
        sys.exit(1)

    logging.basicConfig(format='%(asctime)s::%(levelname)s::%(message)s')
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    with open(args.file, 'r') as contents:
        tm = finduser.TaskManager()
        i = 0
        for line in contents:
            i += 1
            if i <= args.start:
                logging.debug("Skipping current entry: %d, waiting for #%d." % (i, args.start))
                continue
            while len(tm.get_running()) >= args.workers:
                bulk_insert(tm.get_finished())
                time.sleep(0.1)
                logging.warning("Max worker limit reached, waiting...")
            tm.add_task(task.Async("%s %s" % (args.execute, line)))
