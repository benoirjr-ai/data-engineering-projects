import logging 

def get_logger(name):
    """Create and configure a pipeline logger"""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    return logging.getLogger(name)