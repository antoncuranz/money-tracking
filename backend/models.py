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
    teller_access_token = CharField()
    name = CharField()
    institution = CharField()


class Transaction(BaseModel):
    id = AutoField()
    account = ForeignKeyField(Account, backref='transactions')
    teller_id = CharField(unique=True)
    date = DateField(default=datetime.date.today)
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
