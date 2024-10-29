def test_get_amount(transaction_service):
    assert transaction_service.get_amount("123.45") == 12345
    assert transaction_service.get_amount("-123.45") == -12345

    assert transaction_service.get_amount("4.0") == 400
    assert transaction_service.get_amount("4.1") == 410
    assert transaction_service.get_amount("123.") == 12300
    assert transaction_service.get_amount("123") == 12300
    assert transaction_service.get_amount(".5") == 50
    assert transaction_service.get_amount(".51") == 51
    assert transaction_service.get_amount("-.51") == -51
