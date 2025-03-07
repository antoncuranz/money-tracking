import datetime
from decimal import Decimal
from typing import List, Optional, Annotated

from fastapi import Depends

from backend.core.dataaccess.account_repository import AccountRepository
from backend.core.dataaccess.credit_repository import CreditRepository
from backend.core.dataaccess.exchange_repository import ExchangeRepository
from backend.core.dataaccess.payment_repository import PaymentRepository
from backend.core.dataaccess.transaction_repository import TransactionRepository
from backend.models import Transaction, User, Account, Payment, ExchangePayment, Exchange, BaseModel, CreditTransaction, \
    Credit, BankAccount


class Store:
    def __init__(
            self,
            account_repository: Annotated[AccountRepository, Depends()],
            transaction_repository: Annotated[TransactionRepository, Depends()],
            credit_repository: Annotated[CreditRepository, Depends()],
            payment_repository: Annotated[PaymentRepository, Depends()],
            exchange_repository: Annotated[ExchangeRepository, Depends()]
    ):
        self.account_repository = account_repository
        self.transaction_repository = transaction_repository
        self.credit_repository = credit_repository
        self.payment_repository = payment_repository
        self.exchange_repository = exchange_repository
        
    #### ACCOUNTS ####
    
    def get_accounts_of_user(self, user: User) -> List[Account]:
        return self.account_repository.get_accounts_of_user(user)

    def get_bank_accounts_of_user(self, user: User) -> List[BankAccount]:
        return self.account_repository.get_bank_accounts_of_user(user)

    #### TRANSACTIONS ####
    
    def get_transaction(self, user: User, tx_id: int) -> Optional[Transaction]:
        return self.transaction_repository.get_transaction(user, tx_id)

    def get_transactions(self, user: User, account_id: int = None, paid: bool | None = None) -> List[Transaction]:
        return self.transaction_repository.get_transactions(user, account_id, paid)

    def get_paid_transactions_by_payment(self, user: User, payment_id: int) -> List[Transaction]:
        return self.transaction_repository.get_paid_transactions_by_payment(user, payment_id)

    def get_posted_transactions_by_account(self, account_id: int) -> List[Transaction]:
        return self.transaction_repository.get_posted_transactions_by_account(account_id)
    
    def get_posted_transaction_amount(self, account_id: int) -> int:
        return self.transaction_repository.get_posted_transaction_amount(account_id)

    def get_pending_transaction_amount(self, account_id: int) -> int:
        return self.transaction_repository.get_pending_transaction_amount(account_id)
    
    def get_all_posted_transactions(self) -> List[Transaction]:
        return self.transaction_repository.get_all_posted_transactions()

    def get_balance_pending(self) -> int:
       return self.transaction_repository.get_balance_pending()
    
    def get_fees_and_risk_eur(self) -> int:
        return self.transaction_repository.get_fees_and_risk_eur()

    #### PAYMENTS ####

    def get_payment(self, user: User, payment_id: int) -> Optional[Payment]:
        return self.payment_repository.get_payment(user, payment_id)

    def get_payments(self, user: User, account_id: int, processed: bool | None = None) -> List[Payment]:
        return self.payment_repository.get_payments(user, account_id, processed)

    def get_unprocessed_payment(self, payment_id: int) -> Optional[Payment]:
        return self.payment_repository.get_unprocessed_payment(payment_id)

    def get_posted_payment_amount(self, account_id: int) -> int:
        return self.payment_repository.get_posted_payment_amount(account_id)
    
    def get_all_posted_payments(self) -> List[Payment]:
        return self.payment_repository.get_all_posted_payments()

    #### EXCHANGES ####

    def get_exchanges(self, usable=None) -> List[Exchange]:
        return self.exchange_repository.get_exchanges(usable)

    def get_exchange(self, exchange_id: int) -> Optional[Exchange]:
        return self.exchange_repository.get_exchange(exchange_id)
    
    def create_exchange(self, date: datetime.date, amount_usd: int, exchange_rate: Decimal, amount_eur: int, paid_eur: int, fees_eur: int) -> Exchange:
        return self.exchange_repository.create_exchange(date, amount_usd, exchange_rate, amount_eur, paid_eur, fees_eur)
    
    def get_exchange_payments_by_exchange(self, exchange_id: int) -> List[ExchangePayment]:
        return self.exchange_repository.get_exchange_payments_by_exchange(exchange_id)

    def get_exchange_payments_by_payment(self, payment_id: int) -> List[ExchangePayment]:
        return self.exchange_repository.get_exchange_payments_by_payment(payment_id)

    def get_exchange_payment_amount(self, exchange_id: int, payment_id: int) -> int:
        return self.exchange_repository.get_exchange_payment_amount(exchange_id, payment_id)

    def delete_exchange_payment(self, exchange_id: int, payment_id: int):
        self.exchange_repository.delete_exchange_payment(exchange_id, payment_id)
        
    def get_or_create_exchange_payment(self, exchange_id: int, payment_id: int, amount: int) -> tuple[ExchangePayment, bool]:
        return self.exchange_repository.get_or_create_exchange_payment(exchange_id, payment_id, amount)

    #### CREDITS ####

    def get_credit(self, account_id: int, credit_id: int) -> Optional[Credit]:
        return self.credit_repository.get_credit(account_id, credit_id)

    def get_credits(self, user: User, account_id: int, usable: bool | None = None) -> List[Credit]:
        return self.credit_repository.get_credits(user, account_id, usable)

    def get_all_credits(self) -> List[Credit]:
        return self.credit_repository.get_all_credits()

    def get_posted_credit_amount(self, account_id: int) -> int:
        return self.credit_repository.get_posted_credit_amount(account_id)
    
    def get_credit_transaction(self, credit_id: int, transaction_id: int) -> Optional[CreditTransaction]:
        return self.credit_repository.get_credit_transaction(credit_id, transaction_id)

    def get_credit_transactions_by_credit(self, credit_id: int) -> List[CreditTransaction]:
        return self.credit_repository.get_credit_transactions_by_credit(credit_id)

    def get_credit_transactions_by_transaction(self, transaction_id: int) -> List[CreditTransaction]:
        return self.credit_repository.get_credit_transactions_by_transaction(transaction_id)
    
    def get_or_create_credit_transaction(self, credit_id: int, transaction_id: int, amount: int) -> tuple[CreditTransaction, bool]:
        return self.credit_repository.get_or_create_credit_transaction(credit_id, transaction_id, amount)
    
    def delete_credit_transaction(self, credit_id: int, transaction_id: int):
        self.credit_repository.delete_credit_transaction(credit_id, transaction_id)

    ####

    def save(self, model: BaseModel):
        model.save()

    def delete(self, model: BaseModel):
        model.delete_instance()
