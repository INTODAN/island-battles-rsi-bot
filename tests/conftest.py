from collections.abc import Generator

import pytest

from league_tools import store


@pytest.fixture(autouse=True)
def no_match_store(monkeypatch: pytest.MonkeyPatch) -> Generator[None]:
    """Every test starts without a match store, whatever this machine sets: a test that uses one sets it."""
    for name in (store.STORE_VARIABLE, store.MODE_VARIABLE, store.WAIT_VARIABLE, store.FUNCTION_VARIABLE):
        monkeypatch.delenv(name, raising=False)
    yield
