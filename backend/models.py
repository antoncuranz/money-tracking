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


class Payment(BaseModel):
    id = AutoField()
    account = ForeignKeyField(Account, backref="transactions")
    teller_id = CharField(unique=True)
    actual_id = CharField(null=True)
    date = DateField(default=datetime.date.today)
    counterparty = CharField()
    description = CharField()
    category = CharField()
    amount_usd = IntegerField()
    amount_eur = IntegerField(null=True)
    processed = BooleanField(default=False)


class Exchange(BaseModel):
    id = AutoField()
    actual_id = CharField(null=True)
    date = DateField(default=datetime.date.today)
    amount_usd = IntegerField()
    amount_eur = IntegerField()
    exchange_rate = DecimalField()  # needs to be IBKR rate

    # optional, if available:
    # exchange_fee_eur = IntegerField(null=True)


class ExchangePayment(BaseModel):
    class Meta:
        primary_key = CompositeKey("exchange", "payment")

    exchange = ForeignKeyField(Exchange)
    payment = ForeignKeyField(Payment)
    amount = IntegerField()


class Transaction(BaseModel):
    id = AutoField()
    account = ForeignKeyField(Account, backref="transactions")
    teller_id = CharField(unique=True)
    actual_id = CharField(null=True)
    date = DateField(default=datetime.date.today)
    counterparty = CharField()
    description = CharField()
    category = CharField()
    amount_usd = IntegerField()
    amount_eur = IntegerField(null=True)
    status = IntegerField()
    payment = ForeignKeyField(Payment, backref="transactions", null=True)
    ccy_risk = IntegerField(null=True)
    fx_fees = IntegerField(null=True)

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
        POSTED = 2  # only state in which amount_eur can be modified
        PAID = 3


class Credit(BaseModel):
    id = AutoField()
    account = ForeignKeyField(Account, backref="credits")
    teller_id = CharField(unique=True)
    date = DateField(default=datetime.date.today)
    counterparty = CharField()
    description = CharField()
    category = CharField()
    amount_usd = IntegerField()


class CreditTransaction(BaseModel):
    class Meta:
        primary_key = CompositeKey("credit", "transaction")

    credit = ForeignKeyField(Credit)
    transaction = ForeignKeyField(Transaction)
    amount = IntegerField()


class ExchangeRate(BaseModel):
    class Meta:
        primary_key = CompositeKey("date", "source")

    date = DateField(default=datetime.date.today)
    source = IntegerField()
    exchange_rate = DecimalField()

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
