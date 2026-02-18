import pytest

from utils import parse_hhmm


def test_parse_hhmm_ok():
    assert parse_hhmm("09:30") == (9, 30)


@pytest.mark.parametrize("bad", ["25:00", "11:99", "abc", "10-20"])
def test_parse_hhmm_bad(bad):
    with pytest.raises(ValueError):
        parse_hhmm(bad)
