from datetime import datetime

import pytest


@pytest.fixture
def datetime_now() -> datetime:
    return datetime.now()
