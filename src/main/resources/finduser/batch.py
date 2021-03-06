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
import argparse
import time
import multiprocessing
import os

import finduser.data
import settings
import finduser.plugin
import finduser.web


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

    logging.basicConfig(format=settings.log_format)
    logging.getLogger().setLevel(getattr(logging, settings.log_level.upper()))
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    dao = finduser.data.Access(settings.db_default_properties, settings.db_dirty_user_refresh)
    plugins = finduser.plugin.Manager(os.path.join(os.path.dirname(os.path.realpath(__file__)), settings.plugins_path))

    for k, v in plugins.get_plugins().items():
        dao.generate_model(k, v.get_schema())

    logging.info("Starting web server...")
    webserver = multiprocessing.Process(target=finduser.web.main, args=(dao, plugins))
    webserver.start()

    while True:
        # Get the list of dirty users which represent users with tainted
        # or outdated info, and freshen their data by querying GTM directly

        update_count = 0

        """In yer face GIL!"""
        with multiprocessing.Pool(args.workers) as proc_pool:
            for i in proc_pool.imap_unordered(plugins.find_all, dao.get_dirty_users()):
                personId, results = i
                try:
                    dao.update(personId, results)
                    update_count += 1
                except IOError:
                    logging.critical("Critical error found while trying to update the database.")
                    import sys
                    sys.exit(1)
            proc_pool.close()
            proc_pool.join()

        logging.info("Updated %d users, taking a nap..." % (update_count))
        time.sleep(5)
    os.kill(webserver.pid)


if __name__ == '__main__':
    main()
