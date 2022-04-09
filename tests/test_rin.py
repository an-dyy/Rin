from rin import __version__, version


def test_version() -> None:
    assert __version__ == "0.2.0-alpha"

    assert version.major == 0
    assert version.minor == 2
    assert version.patch == 0
    assert version.id == "alpha"
