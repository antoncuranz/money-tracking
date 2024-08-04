ACCOUNT_1 = dict(
    actual_id="actual_test_acc_1", teller_id="teller_test_acc_1", name="Test Account 1", institution="Institution 1"
)

TELLER_TX_1 = dict(
    id="teller_test_tx_1", date="2024-01-01", description="posted tx", amount="10.00", status="posted",
    type="card_payment", details=dict(counterparty=dict(name="counterparty"), category="category")
)
TELLER_TX_2 = dict(
    id="teller_test_tx_2", date="2024-01-02", description="pending tx", amount="10.00", status="pending",
    type="transaction", details=dict(counterparty=dict(name="counterparty"), category="category")
)
TELLER_TX_3 = dict(
    id="teller_test_tx_3", date="2024-01-03", description="posted credit", amount="-10.00", status="posted",
    type="transaction", details=dict(counterparty=dict(name="counterparty"), category="category")
)
TELLER_TX_4 = dict(
    id="teller_test_tx_4", date="2024-01-04", description="pending credit", amount="-10.00", status="pending",
    type="transaction", details=dict(counterparty=dict(name="counterparty"), category="category")
)
TELLER_TX_5 = dict(
    id="teller_test_tx_5", date="2024-01-05", description="posted payment", amount="-10.00", status="posted",
    type="payment", details=dict(counterparty=dict(name="counterparty"), category="category")
)
TELLER_TX_6 = dict(
    id="teller_test_tx_6", date="2024-01-06", description="pending payment", amount="-10.00", status="pending",
    type="payment", details=dict(counterparty=dict(name="counterparty"), category="category")
)

TELLER_TRANSACTIONS = [
    TELLER_TX_1, TELLER_TX_2, TELLER_TX_3, TELLER_TX_4, TELLER_TX_5, TELLER_TX_6
]

TX_1 = dict(
    account_id=1, teller_id="teller_test_tx_1", date="2024-01-01", counterparty="counterparty1",
    description="description1", category="category", amount_usd=1000, status=2
)
TX_2 = dict(
    account_id=1, teller_id="teller_test_tx_2", date="2024-01-02", counterparty="counterparty2",
    description="description2", category="category", amount_usd=500, status=2
)
TX_3 = dict(
    account_id=1, teller_id="teller_test_tx_3", date="2024-01-03", counterparty="counterparty3",
    description="description3", category="category", amount_usd=2000, status=2
)

TRANSACTIONS = [
    TX_1, TX_2, TX_3
]

CREDIT_1 = dict(
    account_id=1, teller_id="teller_test_cr_1", date="2024-01-15", counterparty="Onlineshop", description="Refund",
    category="generic", amount_usd=1000
)

PAYMENT_1 = dict(
    account_id=1, teller_id="teller_test_pm_1", date="2024-01-30", counterparty="Capital One", description="Payment",
    category="generic", amount_usd=sum([tx["amount_usd"] for tx in TRANSACTIONS])
)

EXCHANGE_1 = dict(
    date="2024-01-29", amount_usd=PAYMENT_1["amount_usd"], amount_eur=PAYMENT_1["amount_usd"], exchange_rate=1
)

EXCHANGE_PAYMENT_1 = dict(
    exchange_id=1, payment_id=1, amount=PAYMENT_1["amount_usd"]
)