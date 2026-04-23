from unittest.mock import patch

from olho_publico_etl.storage.r2 import make_r2_client, r2_endpoint_url


def test_r2_endpoint_url_builds_correct_host():
    assert r2_endpoint_url("abc123") == "https://abc123.r2.cloudflarestorage.com"


def test_make_r2_client_configures_boto3():
    with patch("olho_publico_etl.storage.r2.boto3") as boto3:
        make_r2_client("acc", "key", "sec")
        boto3.client.assert_called_once()
        kwargs = boto3.client.call_args.kwargs
        assert kwargs["service_name"] == "s3"
        assert kwargs["endpoint_url"] == "https://acc.r2.cloudflarestorage.com"
        assert kwargs["aws_access_key_id"] == "key"
        assert kwargs["aws_secret_access_key"] == "sec"
        assert kwargs["region_name"] == "auto"
