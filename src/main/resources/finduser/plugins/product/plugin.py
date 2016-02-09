#!/usr/bin/env python

import logging
import os

import finduser.plugin


class Find(finduser.plugin.Plugin):

    def __init__(self):
        super().__init__()
        logging.info("GTM Product finder initialized.")
        self.command = 'python ' + os.path.join(os.path.dirname(__file__), 'simulate.py')

    def get_schema(self):
        return {
            "accNumber": 'str',
            "openDate": 'date',
            "amountEuro": 'float',
            "balanceEuro": 'float',
            "intervType": 'int',
            "titDesc": 'str',
            "accDesc": 'str',
            "statusCode": 'int',
            "statusDesc": 'str',
            "residencia": 'int',
            "alias": 'str',
            "corpId": 'int',
            "productSubtype": 'str',
            "associatedAccount": 'str',
            "holdBalance": 'float',
            "accBlocked": 'bool',
            "creditLimit": 'float',
            "realAmount": 'float',
            "partialCancellable": 'bool',
            "moreInterveners": 'bool',
            "iban": 'str',
            "enableAlias": 'bool',
        }
