from datetime import date, timedelta

from messages import relationship_days_text


def test_relationship_days_text_future_date():
    text = relationship_days_text(date.today() + timedelta(days=1))
    assert "هنوز نرسیده" in text


def test_relationship_days_text_normal_date():
    text = relationship_days_text(date.today() - timedelta(days=400))
    assert "400 روز" in text
