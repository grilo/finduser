#!/usr/bin/env python

import logging
import sys


def check():
    if sys.version_info < (3, 5):
        logging.critical("Sorry, Python >=3.5.x is required.")
        sys.exit(1)

if __name__ == '__main__':
    check()
