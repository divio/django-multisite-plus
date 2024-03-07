import pytest

from django_multisite_plus import fastrouter_lookup


def test_get_nonexisting():
    with pytest.raises(RuntimeError):
        fastrouter_lookup.get(b"test.com")
