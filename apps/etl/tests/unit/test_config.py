import os
from unittest.mock import patch

import pytest

from olho_publico_etl.config import Settings, get_settings, require_settings


def test_settings_defaults_ok():
    s = Settings()
    assert s.database_url.startswith("postgresql://")


def test_require_settings_passes_with_all_set():
    with patch.dict(os.environ, {
        "TRANSPARENCIA_API_KEY": "abc",
        "R2_ACCOUNT_ID": "acc",
        "R2_ACCESS_KEY_ID": "key",
        "R2_SECRET_ACCESS_KEY": "sec",
    }, clear=False):
        get_settings.cache_clear()
        require_settings("transparencia_api_key", "r2_account_id")  # não levanta


def test_require_settings_raises_when_missing():
    get_settings.cache_clear()
    with patch.dict(os.environ, {"TRANSPARENCIA_API_KEY": ""}, clear=False):
        get_settings.cache_clear()
        with pytest.raises(RuntimeError, match="transparencia_api_key"):
            require_settings("transparencia_api_key")
