from src.pipeline import run_incremental_pipeline
from src.database import create_connection


def test_pipeline_processes_new_transactions(tmp_path):
    # Arrange
    state_file = tmp_path / "watermark.txt"

    # Act
    result = run_incremental_pipeline(
        "data/transactions.csv",
        state_file
    )

    # Assert
    assert result == 1006


def test_pipeline_does_not_reprocess_transactions(tmp_path):
    # Arrange
    state_file = tmp_path / "watermark.txt"

    # First run.
    first_result = run_incremental_pipeline(
        "data/transactions.csv",
        state_file
    )

    # Second run.
    second_result = run_incremental_pipeline(
        "data/transactions.csv",
        state_file
    )

    # Assert.
    assert first_result == 1006
    assert second_result == 1006


def test_pipeline_does_not_update_watermark_when_load_fails(
    tmp_path,
    monkeypatch
):
    state_file = tmp_path / "watermark.txt"

    # Start with watermark at 1005.
    state_file.write_text("1005")

    def failing_load(connection, transactions):
        raise RuntimeError("Database load failed")

    monkeypatch.setattr(
        "src.pipeline.load_transactions",
        failing_load
    )

    try:
        run_incremental_pipeline(
            "data/transactions.csv",
            state_file
        )
    except RuntimeError:
        pass

    # The watermark must remain unchanged.
    assert state_file.read_text() == "1005"