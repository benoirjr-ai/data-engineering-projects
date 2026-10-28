from src.logging_config import get_logger


def test_get_logger():
    logger = get_logger("test_pipeline")

    assert logger.name == "test_pipeline"
    assert logger.level == 0