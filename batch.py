#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Find user utility.


The goal is to run multiple command line utilities and insert them into a
RDBMS. This will allow us to find users with specific characteristics as
test case data based on "real" (ciphered/masked) information.

Example:
    All of the command line parameters are optional, defaults are retrieved
    from settings.py

        $ python batch.py -w 16 -x 'java -jar finduser.jar' -v

    https://github.com/grilo/finduser
"""

import logging
logging.basicConfig(format='%(asctime)s::%(levelname)s::%(message)s')
import argparse
import time

import finduser.product
import finduser.data
import settings


def main():
    """Main method."""

    desc = 'Execute several utilities and insert the output into a database.'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument("-v", "--verbose", action="store_true", \
        help="Increase output verbosity")
    parser.add_argument("-w", "--workers", type=int, \
        default=settings.batch_default_workers, \
        help="Amount of subprocesses to launch which will execute the script")
    parser.add_argument("-x", "--execute", default=settings.batch_find_user_exec, \
        help="The utility to be executed (fixed parameters may be specified).")

    args = parser.parse_args()

    logging.getLogger().setLevel(logging.INFO)
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    gtm_product = finduser.product.GTM(args.execute, args.workers, settings.default_encoding)
    dao = finduser.data.Access(settings.db_default_properties, settings.db_dirty_user_refresh)

    while True:
        # Get the list of dirty users which represent users with tainted
        # or outdated info, and freshen their data by querying GTM directly
        for products in gtm_product.parallel_find(dao.get_dirty_users()):
            dao.update_products(products)

        logging.info("All users processed, taking a nap...")
        time.sleep(5)


if __name__ == '__main__':
    main()

