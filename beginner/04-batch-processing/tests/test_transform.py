from src.transform import transform_batch


def test_completed_transaction_is_transformed():
    batch = [
        {
            "transaction_id": "1001",
            "customer_id": "C001",
            "transaction_date": "2026-09-01",
            "amount": "125.50",
            "category": "Electronics",
            "status": "completed"
        }
    ]

    result = transform_batch(batch)

    assert len(result) == 1
    assert result[0]["transaction_id"] == 1001
    assert result[0]["amount"] == 125.50


def test_cancelled_transaction_is_removed():
    batch = [
        {
            "transaction_id": "1001",
            "customer_id": "C001",
            "transaction_date": "2026-09-01",
            "amount": "125.50",
            "category": "Electronics",
            "status": "completed"
        },
        {
            "transaction_id": "1004",
            "customer_id": "C003",
            "transaction_date": "2026-09-01",
            "amount": "50.00",
            "category": "Clothing",
            "status": "cancelled"
        }
    ]

    result = transform_batch(batch)

    assert len(result) == 1
    assert result[0]["transaction_id"] == 1001

    

def test_transaction_data_types_are_converted():
    batch = [
        {
            "transaction_id": "1001",
            "customer_id": "C001",
            "transaction_date": "2026-09-01",
            "amount": "125.50",
            "category": "Electronics",
            "status": "completed"
        }
    ]

    result = transform_batch(batch)

    assert isinstance(result[0]["transaction_id"], int)
    assert isinstance(result[0]["amount"], float)