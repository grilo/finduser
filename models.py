import logging
import extlibs.peewee as orm

import settings

db = orm.SqliteDatabase(settings.db_name, pragmas=(
        ("busy_timeout", "30000"),
    )
)

class BaseModel(orm.Model):
    class Meta:
        database = db

class User(BaseModel):
    cip = orm.BigIntegerField(primary_key=True)
    dirty = orm.BooleanField(default=True)
    lastUpdate = orm.DateTimeField(null=True)

class Product(BaseModel):
    user = orm.ForeignKeyField(User, related_name='products')
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

    def python_schema(self):
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

