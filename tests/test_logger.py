from rin import logger


def test_logger():
    log = logger.create("test")

    assert hasattr(logger, "create")
    assert hasattr(logger, "ColouredStreamHandler")

    assert log.name == "test"
    assert log.level == 10
    assert isinstance(log.handlers[0], logger.ColouredStreamHandler)
