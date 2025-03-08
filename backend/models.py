import datetime
from decimal import Decimal
from enum import Enum
from typing import List

from sqlmodel import create_engine, Session, SQLModel, Relationship, Field

from backend.config import config

database_url = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(
    config.postgres_user, config.postgres_password, config.postgres_host, config.postgres_port, config.postgres_database
)
engine = create_engine(database_url)


def get_session():
    with Session(engine) as session:
        yield session


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    super_user: bool = False
    actual_sync_id: str | None
    actual_encryption_password: str | None


class BankAccount(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship()
    accounts: List["Account"] = Relationship()
    name: str
    institution: str
    icon: str | None
    balance: int = 0
    import_id: str | None


class Account(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship()
    bank_account_id: int | None = Field(foreign_key="bankaccount.id")
    bank_account: BankAccount | None = Relationship(back_populates="accounts")
    actual_id: str | None
    import_id: str | None
    name: str
    institution: str
    due_day: int | None
    autopay_offset: int | None
    icon: str | None
    color: str | None
    target_spend: int | None


class Payment(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="account.id")
    account: Account = Relationship()
    import_id: str | None = Field(unique=True)
    actual_id: str | None
    date: datetime.date = datetime.date.today
    counterparty: str
    description: str
    category: str | None
    amount_usd: int
    amount_eur: int | None
    status: int
    exchanges: List["ExchangePayment"] = Relationship(cascade_delete=True)
    transactions: List["Transaction"] = Relationship()

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


class Exchange(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    date: datetime.date = datetime.date.today
    amount_usd: int
    exchange_rate: Decimal = Field(decimal_places=8)
    amount_eur: int | None
    paid_eur: int
    fees_eur: int | None
    import_id: str | None = Field(unique=True)
    actual_id: str | None = Field(unique=True)
    payments: List["ExchangePayment"] = Relationship(cascade_delete=True)


class ExchangePayment(SQLModel, table=True):
    exchange_id: int = Field(primary_key=True, foreign_key="exchange.id")
    exchange: Exchange = Relationship(back_populates="payments")
    payment_id: int = Field(primary_key=True, foreign_key="payment.id")
    payment: Payment = Relationship(back_populates="exchanges")
    amount: int


class TransactionBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="account.id")
    payment_id: int | None = Field(foreign_key="payment.id")
    import_id: str = Field(unique=True)
    actual_id: str | None
    date: datetime.date = datetime.date.today
    counterparty: str
    description: str
    category: str | None
    amount_usd: int
    amount_eur: int | None
    status: int
    fees_and_risk_eur: int | None
    ignore: bool | None = False

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


class Transaction(TransactionBase, table=True):
    account: Account = Relationship()
    payment: Payment | None = Relationship(back_populates="transactions")
    credits: List["CreditTransaction"] = Relationship()


class TransactionWithGuessedAmount(TransactionBase):
    guessed_amount_eur: int | None
    credits: List["CreditTransaction"]
    

class Credit(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="account.id")
    account: Account = Relationship()
    import_id: str = Field(unique=True)
    date: datetime.date = datetime.date.today
    counterparty: str
    description: str
    category: str | None
    amount_usd: int
    transactions: List["CreditTransaction"] = Relationship()


class CreditTransaction(SQLModel, table=True):
    credit_id: int = Field(primary_key=True, foreign_key="credit.id")
    credit: Credit = Relationship(back_populates="transactions")
    transaction_id: int = Field(primary_key=True, foreign_key="transaction.id")
    transaction: Transaction = Relationship(back_populates="credits")
    amount: int


class ExchangeRate(SQLModel, table=True):
    date: datetime.date = Field(primary_key=True, default=datetime.date.today)
    source: int = Field(primary_key=True)
    exchange_rate: Decimal = Field(decimal_places=8)

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

