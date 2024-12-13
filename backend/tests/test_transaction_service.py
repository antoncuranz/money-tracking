def test_get_amount(teller_service):
    assert teller_service.get_amount("123.45") == 12345
    assert teller_service.get_amount("-123.45") == -12345

    assert teller_service.get_amount("4.0") == 400
    assert teller_service.get_amount("4.1") == 410
    assert teller_service.get_amount("123.") == 12300
    assert teller_service.get_amount("123") == 12300
    assert teller_service.get_amount(".5") == 50
    assert teller_service.get_amount(".51") == 51
    assert teller_service.get_amount("-.51") == -51
