import datetime
from decimal import Decimal
from typing import List, Optional, Annotated

from fastapi import Depends
from sqlmodel import Session

from core.dataaccess.account_repository import AccountRepository
from core.dataaccess.credit_repository import CreditRepository
from core.dataaccess.exchange_repository import ExchangeRepository
from core.dataaccess.payment_repository import PaymentRepository
from core.dataaccess.transaction_repository import TransactionRepository
from models import Transaction, User, Account, Payment, ExchangePayment, Exchange, CreditTransaction, \
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
    
    def get_all_accounts(self, session: Session) -> List[Account]:
        return self.account_repository.get_all_accounts(session)

    def get_accounts_of_user(self, session: Session, user: User) -> List[Account]:
        return self.account_repository.get_accounts_of_user(session, user)
    
    def get_account(self, session: Session, user: User, account_id: int) -> Optional[Account]:
        return self.account_repository.get_account(session, user, account_id)

    def create_account(self, session: Session, user: User, bank_account_id: int | None, actual_id: int | None,
                       plaid_account_id: int | None, name: str, institution: str, due_day: int | None,
                       autopay_offset: int | None, icon: str | None, color: str | None, target_spend: int | None) -> Account:
        return self.account_repository.create_account(session, user, bank_account_id=bank_account_id, actual_id=actual_id,
                          plaid_account_id=plaid_account_id, name=name, institution=institution, due_day=due_day,
                          autopay_offset=autopay_offset, icon=icon, color=color, target_spend=target_spend)

    def get_all_bank_accounts(self, session: Session) -> List[BankAccount]:
        return self.account_repository.get_all_bank_accounts(session)
    
    def get_bank_accounts_of_user(self, session: Session, user: User) -> List[BankAccount]:
        return self.account_repository.get_bank_accounts_of_user(session, user)
    
    def get_bank_account(self, session: Session, user: User, bank_account_id: int) -> Optional[BankAccount]:
        return self.account_repository.get_bank_account(session, user, bank_account_id)

    def create_bank_account(self, session: Session, user: User, name: str, institution: str, icon: str | None, plaid_account_id: int | None) -> BankAccount:
        return self.account_repository.create_bank_account(session, user, name=name, institution=institution, icon=icon, plaid_account_id=plaid_account_id)

    #### TRANSACTIONS ####
    
    def get_transaction(self, session: Session, user: User, tx_id: int) -> Optional[Transaction]:
        return self.transaction_repository.get_transaction(session, user, tx_id)

    def get_transactions(self, session: Session, user: User, account_id: int = None, paid: bool | None = None) -> List[Transaction]:
        return self.transaction_repository.get_transactions(session, user, account_id, paid)

    def get_paid_transactions_by_payment(self, session: Session, payment_id: int) -> List[Transaction]:
        return self.transaction_repository.get_paid_transactions_by_payment(session, payment_id)

    def get_posted_transactions_by_account(self, session: Session, account_id: int) -> List[Transaction]:
        return self.transaction_repository.get_posted_transactions_by_account(session, account_id)
    
    def get_posted_transaction_amount(self, session: Session, account_id: int) -> int:
        return self.transaction_repository.get_posted_transaction_amount(session, account_id)

    def get_pending_transaction_amount(self, session: Session, account_id: int) -> int:
        return self.transaction_repository.get_pending_transaction_amount(session, account_id)
    
    def get_all_posted_transactions(self, session: Session) -> List[Transaction]:
        return self.transaction_repository.get_all_posted_transactions(session)

    def get_balance_pending(self, session: Session) -> int:
       return self.transaction_repository.get_balance_pending(session)
    
    def get_fees_and_risk_eur(self, session: Session) -> int:
        return self.transaction_repository.get_fees_and_risk_eur(session)

    #### PAYMENTS ####

    def get_payment_unsafe(self, session: Session, payment_id: int) -> Optional[Payment]:
        return self.payment_repository.get_payment_unsafe(session, payment_id)

    def get_payments(self, session: Session, user: User, account_id: int, processed: bool | None = None) -> List[Payment]:
        return self.payment_repository.get_payments(session, user, account_id, processed)

    def get_unprocessed_payment(self, session: Session, payment_id: int) -> Optional[Payment]:
        return self.payment_repository.get_unprocessed_payment(session, payment_id)

    def get_posted_payment_amount(self, session: Session, account_id: int) -> int:
        return self.payment_repository.get_posted_payment_amount(session, account_id)

    def get_all_posted_payments(self, session: Session) -> List[Payment]:
        return self.payment_repository.get_all_posted_payments(session)

    #### EXCHANGES ####

    def get_exchanges(self, session: Session, usable=None) -> List[Exchange]:
        return self.exchange_repository.get_exchanges(session, usable)

    def get_exchange(self, session: Session, exchange_id: int) -> Optional[Exchange]:
        return self.exchange_repository.get_exchange(session, exchange_id)

    def create_exchange(self, session: Session, date: datetime.date, amount_usd: int, exchange_rate: Decimal, amount_eur: int, paid_eur: int, fees_eur: int) -> Exchange:
        return self.exchange_repository.create_exchange(session, date, amount_usd, exchange_rate, amount_eur, paid_eur, fees_eur)

    def get_exchange_payments_by_exchange(self, session: Session, exchange_id: int) -> List[ExchangePayment]:
        return self.exchange_repository.get_exchange_payments_by_exchange(session, exchange_id)

    def get_exchange_payments_by_payment(self, session: Session, payment_id: int) -> List[ExchangePayment]:
        return self.exchange_repository.get_exchange_payments_by_payment(session, payment_id)

    def get_exchange_payment_amount(self, session: Session, exchange_id: int, payment_id: int) -> int:
        return self.exchange_repository.get_exchange_payment_amount(session, exchange_id, payment_id)

    def delete_exchange_payment(self, session: Session, exchange_id: int, payment_id: int):
        self.exchange_repository.delete_exchange_payment(session, exchange_id, payment_id)

    def get_or_create_exchange_payment(self, session: Session, exchange_id: int, payment_id: int, amount: int) -> tuple[ExchangePayment, bool]:
        return self.exchange_repository.get_or_create_exchange_payment(session, exchange_id, payment_id, amount)

    #### CREDITS ####

    def get_credit(self, session: Session, account_id: int, credit_id: int) -> Optional[Credit]:
        return self.credit_repository.get_credit(session, account_id, credit_id)

    def get_credits(self, session: Session, user: User, account_id: int, usable: bool | None = None) -> List[Credit]:
        return self.credit_repository.get_credits(session, user, account_id, usable)

    def get_all_credits(self, session: Session) -> List[Credit]:
        return self.credit_repository.get_all_credits(session)

    def get_posted_credit_amount(self, session: Session, account_id: int) -> int:
        return self.credit_repository.get_posted_credit_amount(session, account_id)

    def get_credit_transaction(self, session: Session, credit_id: int, transaction_id: int) -> Optional[CreditTransaction]:
        return self.credit_repository.get_credit_transaction(session, credit_id, transaction_id)

    def get_credit_transactions_by_credit(self, session: Session, credit_id: int) -> List[CreditTransaction]:
        return self.credit_repository.get_credit_transactions_by_credit(session, credit_id)

    def get_credit_transactions_by_transaction(self, session: Session, transaction_id: int) -> List[CreditTransaction]:
        return self.credit_repository.get_credit_transactions_by_transaction(session, transaction_id)

    def get_or_create_credit_transaction(self, session: Session, credit_id: int, transaction_id: int, amount: int) -> tuple[CreditTransaction, bool]:
        return self.credit_repository.get_or_create_credit_transaction(session, credit_id, transaction_id, amount)

    def delete_credit_transaction(self, session: Session, credit_id: int, transaction_id: int):
        self.credit_repository.delete_credit_transaction(session, credit_id, transaction_id)
