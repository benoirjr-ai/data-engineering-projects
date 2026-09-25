from src.state import save_watermark, load_watermark


def test_save_and_load_watermark(tmp_path):
    # Arrange
    state_file = tmp_path / "watermark.txt"

    # Act
    save_watermark(state_file, 1005)
    result = load_watermark(state_file)

    # Assert
    assert result == 1005


def test_missing_watermark_returns_zero(tmp_path):
    # Arrange
    state_file = tmp_path / "watermark.txt"

    # Act
    result = load_watermark(state_file)

    # Assert
    assert result == 0