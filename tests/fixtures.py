ACCOUNT_1 = dict(
    actual_id="actual_test_acc_1", teller_id="teller_test_acc_1", name="Test Account 1", institution="Institution 1"
)

TELLER_TX_1 = dict(
    id="teller_test_tx_1", date="2024-01-30", description="description", amount="10.00", status="posted",
    type="transaction", details=dict(counterparty=dict(name="counterparty"), category="category")
)

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

CREDIT_1 = dict(
    account_id=1, teller_id="teller_test_cr_1", date="2024-01-30", counterparty="Onlineshop", description="Refund",
    category="generic", amount_usd=1000
)