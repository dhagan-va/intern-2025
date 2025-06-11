import pytest
from src.config import Setting, load_settings


def test_setting_creation():
    setting = Setting("http://127.0.0.1:5000/270/", 5)
    assert setting.endpoint == "http://127.0.0.1:5000/270/"
    assert setting.rps == 5
