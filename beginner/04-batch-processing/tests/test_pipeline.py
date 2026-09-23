from src.pipeline import run_pipeline


def test_pipeline():
    # Arrange
    file_path = "data/transactions.csv"

    # Act
    result = run_pipeline(file_path, batch_size=3)

    # Assert
    assert result["C001"]["transaction_count"] == 4
    assert result["C001"]["total_amount"] == 610.50

    assert result["C002"]["transaction_count"] == 2
    assert result["C002"]["total_amount"] == 195.00

    assert result["C003"]["transaction_count"] == 1
    assert result["C003"]["total_amount"] == 45.00

    assert result["C004"]["transaction_count"] == 2
    assert result["C004"]["total_amount"] == 800.00

    assert result["C005"]["transaction_count"] == 1
    assert result["C005"]["total_amount"] == 90.00


def test_pipeline_excludes_cancelled_transactions():
    # Arrange
    file_path = "data/transactions.csv"

    # Act
    result = run_pipeline(file_path, batch_size=3)

    # Assert
    # C002 has 3 transactions in the CSV,
    # but one is cancelled.
    assert result["C002"]["transaction_count"] == 2
    assert result["C002"]["total_amount"] == 195.00
    