from src.extract import read_batches


def test_read_batches():
    batches = list(
        read_batches("data/transactions.csv", batch_size=3)
    )

    assert len(batches) == 4

    assert len(batches[0]) == 3
    assert len(batches[1]) == 3
    assert len(batches[2]) == 3
    assert len(batches[3]) == 3


def test_read_batches_with_incomplete_batch():
    batches = list(
        read_batches("data/transactions.csv", batch_size=5)
    )

    assert len(batches) == 3

    assert len(batches[0]) == 5
    assert len(batches[1]) == 5
    assert len(batches[2]) == 2