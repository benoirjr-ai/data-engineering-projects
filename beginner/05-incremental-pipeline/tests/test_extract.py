from src.extract import read_transactions, read_new_transactions

def test_read_transactions():
    transactions = list(
        read_transactions("data/transactions.csv")
    )

    assert len(transactions) == 6


def test_read_only_new_transactions():
    transactions = list(
        read_new_transactions(
            "data/transactions.csv",
            last_processed_id=1003
        )
    )

    assert len(transactions) == 3
    assert transactions[0]["transaction_id"] == "1004"
    assert transactions[1]["transaction_id"] == "1005"
    assert transactions[2]["transaction_id"] == "1006"