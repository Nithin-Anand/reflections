import pytest


@pytest.fixture(autouse=True)
def disable_auto_tag_on_save(settings):
    """Disable background tagging threads in tests to prevent SQLite locking."""
    settings.AUTO_TAG_ON_SAVE = False
