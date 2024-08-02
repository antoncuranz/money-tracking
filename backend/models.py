from peewee import *
import datetime
from enum import Enum

from backend.config import Config

db = SqliteDatabase(Config.database_path)


class BaseModel(Model):
    class Meta:
        database = db


class Account(BaseModel):
    id = AutoField()
    actual_id = CharField()
    teller_id = CharField()
    teller_access_token = CharField(null=True)
    teller_enrollment_id = CharField(null=True)
    name = CharField()
    institution = CharField()


class Transaction(BaseModel):
    id = AutoField()
    account = ForeignKeyField(Account, backref='transactions')
    teller_id = CharField(unique=True)
    actual_id = CharField(null=True)
    date = DateField(default=datetime.date.today)
    counterparty = CharField()
    description = CharField()
    category = CharField()
    amount_usd = IntegerField()
    amount_eur = IntegerField(null=True)
    status = IntegerField()

    @property
    def status_enum(self):
        return Transaction.Status(self.status)

    @status_enum.setter
    def status_enum(self, status):
        if isinstance(status, Transaction.Status):
            self.status = status.value
        else:
            raise ValueError("Invalid status type")

    class Status(Enum):
        PENDING = 1
        POSTED = 2
        IMPORTED = 3


class Exchange(BaseModel):
    id = AutoField()
    date = DateField(default=datetime.date.today)
    amount_usd = IntegerField()
    amount_eur = IntegerField()

    # optional, if available:
    exchange_fee_eur = IntegerField(null=True)
    exchange_rate = IntegerField(null=True)  # needs to be IBKR rate


class Deposit(BaseModel):
    id = AutoField()
    account = ForeignKeyField(Account, backref='transactions')
    teller_id = CharField(unique=True)
    date = DateField(default=datetime.date.today)
    amount_usd = IntegerField()


class ExchangedWith(BaseModel):
    exchange = ForeignKeyField(Exchange, backref="exchanges")
    deposit = ForeignKeyField(Deposit, backref="transactions")
    amount_usd = IntegerField(null=True)


class PaidWith(BaseModel):
    deposit = ForeignKeyField(Deposit, backref="transactions")
    transaction = ForeignKeyField(Transaction, backref="deposits")
    amount_usd = IntegerField(null=True)  # should rarely be non-null (only for statement credits/bonusses)


class ExchangeRate(BaseModel):
    class Meta:
        primary_key = CompositeKey("date", "source")

    date = DateField(default=datetime.date.today)
    source = IntegerField()
    exchange_rate = IntegerField()

    @property
    def source_enum(self):
        return ExchangeRate.Source(self.source)

    @source_enum.setter
    def source_enum(self, status):
        if isinstance(status, ExchangeRate.Source):
            self.source = status.value
        else:
            raise ValueError("Invalid source type")

    class Source(Enum):
        IBKR = 1
        MASTERCARD = 2
