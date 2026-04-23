from unittest.mock import patch

from olho_publico_etl.db.connection import make_pool


def test_make_pool_returns_connection_pool():
    with patch("olho_publico_etl.db.connection.ConnectionPool") as pool_cls:
        make_pool("postgresql://x@y/z")
        pool_cls.assert_called_once()
        conninfo = pool_cls.call_args.kwargs["conninfo"]
        assert conninfo == "postgresql://x@y/z"


def test_make_pool_min_max_sensible_defaults():
    with patch("olho_publico_etl.db.connection.ConnectionPool") as pool_cls:
        make_pool("postgresql://x@y/z")
        kwargs = pool_cls.call_args.kwargs
        assert kwargs["min_size"] == 1
        assert kwargs["max_size"] == 5
