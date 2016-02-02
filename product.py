import logging
import types
import extlibs.peewee as orm

import models

class Product(models.BaseModel):
    user = orm.ForeignKeyField(models.User, related_name='products')
    accNumber = orm.CharField(primary_key=True)
    openDate = orm.DateTimeField(null=False)
    amountEuro = orm.DoubleField(null=False)
    balanceEuro = orm.DoubleField(null=False)
    intervType = orm.IntegerField(null=False)
    titDesc = orm.CharField()
    accDesc = orm.CharField()
    statusCode = orm.IntegerField(null=False)
    statusDesc = orm.CharField()
    residencia = orm.IntegerField(null=False)
    alias = orm.CharField()
    corpId = orm.IntegerField(null=False)
    productSubtype = orm.CharField()
    associatedAccount = orm.CharField()
    holdBalance = orm.DoubleField(null=False)
    accBlocked = orm.BooleanField(null=False)
    creditLimit = orm.DoubleField(null=False)
    realAmount = orm.DoubleField(null=False)
    partialCancellable = orm.BooleanField(null=False)
    moreInterveners = orm.BooleanField(null=False)
    iban = orm.CharField()
    enableAlias = orm.BooleanField(null=False)

def get_schema():

    return {
        "accNumber": str,
        "openDate": float,
        "amountEuro": float,
        "balanceEuro": float,
        "intervType": int,
        "titDesc": str,
        "accDesc": str,
        "statusCode": int,
        "statusDesc": str,
        "residencia": int,
        "alias": str,
        "corpId": int,
        "productSubtype": str,
        "associatedAccount": str,
        "holdBalance": float,
        "accBlocked": bool,
        "creditLimit": float,
        "realAmount": float,
        "partialCancellable": bool,
        "moreInterveners": bool,
        "iban": str,
        "enableAlias": bool,
    }


def validate(json_obj):

    error_count = 0
    for k, v in get_schema().items():
        try:
            assert k in json_obj.keys()
        except AssertionError:
            error_count += 1
            logging.error("Key (%s) doesn't exist in JSON." % (k))
        try:
            assert type(json_obj[k]) == v
        except AssertionError:
            logging.error("Value (%s) is of the wrong type." % (str(json_obj[k])))
    if error_count > 0:
        return False
    return True
