import logging

logger = logging.getLogger(__name__)


class DummyController:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __getattr__(self, item):
        logger.debug(f"get {item}")
        return super().__getattribute__(item)

    def __setattr__(self, key, value):
        logger.debug(f"set {key}: {value}")
        super().__setattr__(key, value)
