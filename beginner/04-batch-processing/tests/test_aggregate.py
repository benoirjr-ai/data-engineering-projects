from src.aggregate import aggregate_batch


def test_same_customer_transactions_are_aggregated():
    # Arrange
    batch = [
        {"customer_id": "C001", "amount": 100.00},
        {"customer_id": "C001", "amount": 200.00}
    ]

    # Act
    result = aggregate_batch(batch)

    # Assert
    assert result["C001"]["transaction_count"] == 2
    assert result["C001"]["total_amount"] == 300.00


def test_multiple_customers_are_aggregated():
    # Arrange
    batch = [
        {"customer_id": "C001", "amount": 100.00},
        {"customer_id": "C002", "amount": 50.00},
        {"customer_id": "C001", "amount": 25.00}
    ]

    # Act
    result = aggregate_batch(batch)

    # Assert
    assert result["C001"]["transaction_count"] == 2
    assert result["C001"]["total_amount"] == 125.00

    assert result["C002"]["transaction_count"] == 1
    assert result["C002"]["total_amount"] == 50.00