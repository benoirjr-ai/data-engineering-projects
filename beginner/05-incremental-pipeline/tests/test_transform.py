from src.transform import transform_transaction


def test_transform_transaction():
    raw_transaction = {
        "transaction_id": "1007",
        "customer_id": " C004 ",
        "transaction_date": "2026-09-06",
        "amount": "300.50",
        "status": "COMPLETED",
    }

    result = transform_transaction(raw_transaction)

    assert result["transaction_id"] == 1007
    assert result["customer_id"] == "C004"
    assert result["transaction_date"] == "2026-09-06"
    assert result["amount"] == 300.50
    assert result["status"] == "completed"