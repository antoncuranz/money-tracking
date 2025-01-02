from peewee import *
import datetime
from enum import Enum

from backend.config import Config

db = PostgresqlDatabase(Config.postgres_database,
                        user=Config.postgres_user, password=Config.postgres_password, host=Config.postgres_host, port=Config.postgres_port)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id = AutoField()
    name = CharField()
    super_user = BooleanField(default=False)
    actual_sync_id = CharField(null=True)
    actual_encryption_password = CharField(null=True)


class BankAccount(BaseModel):
    id = AutoField()
    user = ForeignKeyField(User, backref="bank_accounts")
    name = CharField()
    institution = CharField()
    icon = CharField(null=True)
    balance = IntegerField(default=0)
    import_id = CharField(null=True)


class Account(BaseModel):
    id = AutoField()
    user = ForeignKeyField(User, backref="accounts")
    bank_account = ForeignKeyField(BankAccount, backref="user", null=True)
    actual_id = CharField(null=True)
    import_id = CharField(null=True)
    name = CharField()
    institution = CharField()
    due_day = IntegerField(null=True)
    autopay_offset = IntegerField(null=True)
    icon = CharField(null=True)
    color = CharField(null=True)
    target_spend = IntegerField(null=True)


class Payment(BaseModel):
    id = AutoField()
    account = ForeignKeyField(Account, backref="payments")
    import_id = CharField(unique=True, null=True)
    actual_id = CharField(null=True)
    date = DateField(default=datetime.date.today)
    counterparty = CharField()
    description = CharField()
    category = CharField(null=True)
    amount_usd = IntegerField()
    amount_eur = IntegerField(null=True)
    status = IntegerField()

    @property
    def status_enum(self):
        return Payment.Status(self.status)

    @status_enum.setter
    def status_enum(self, status):
        if isinstance(status, Payment.Status):
            self.status = status.value
        else:
            raise ValueError("Invalid status type")

    class Status(Enum):
        PENDING = 1
        POSTED = 2
        PROCESSED = 3


class Exchange(BaseModel):
    id = AutoField()
    actual_id = CharField(unique=True, null=True)
    date = DateField(default=datetime.date.today)
    amount_usd = IntegerField()
    exchange_rate = DecimalField(decimal_places=8)
    amount_eur = IntegerField(null=True)
    paid_eur = IntegerField()
    fees_eur = IntegerField(null=True)
    import_id = CharField(unique=True, null=True)


class ExchangePayment(BaseModel):
    class Meta:
        primary_key = CompositeKey("exchange", "payment")

    exchange = ForeignKeyField(Exchange, on_delete="CASCADE")
    payment = ForeignKeyField(Payment, on_delete="CASCADE")
    amount = IntegerField()


class Transaction(BaseModel):
    id = AutoField()
    account = ForeignKeyField(Account, backref="transactions")
    import_id = CharField(unique=True)
    actual_id = CharField(null=True)
    date = DateField(default=datetime.date.today)
    counterparty = CharField()
    description = CharField()
    category = CharField(null=True)
    amount_usd = IntegerField()
    amount_eur = IntegerField(null=True)
    status = IntegerField()
    payment = ForeignKeyField(Payment, backref="transactions", null=True)
    fees_and_risk_eur = IntegerField(null=True)
    ignore = BooleanField(null=True)

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
    import_id = CharField(unique=True)
    date = DateField(default=datetime.date.today)
    counterparty = CharField()
    description = CharField()
    category = CharField(null=True)
    amount_usd = IntegerField()


class CreditTransaction(BaseModel):
    class Meta:
        primary_key = CompositeKey("credit", "transaction")

    credit = ForeignKeyField(Credit, on_delete="CASCADE")
    transaction = ForeignKeyField(Transaction, on_delete="CASCADE")
    amount = IntegerField()


class ExchangeRate(BaseModel):
    class Meta:
        primary_key = CompositeKey("date", "source")

    date = DateField(default=datetime.date.today)
    source = IntegerField()
    exchange_rate = DecimalField(decimal_places=8)

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
        EXCHANGERATESIO = 3

ALL_TABLES = [CreditTransaction, Credit, Transaction, ExchangePayment, Exchange, Payment, Account, BankAccount, User, ExchangeRate]
