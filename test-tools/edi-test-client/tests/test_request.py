import pytest
from unittest.mock import patch, Mock
from src.client import reqs

def test_send_270_request_success():
    mock_response = Mock()
    mock_response.status_code = 200
    with patch('src.client.reqs.requests.post', return_value=mock_response) as mock_post:
        status, elapsed = reqs.send_270_request("http://example")
        assert status == 200
        assert elapsed >= 0
        mock_post.assert_called_once_with(url="http://example", data=reqs.samples.SAMPLE_270)

def test_send_270_request_exception():
    with patch('src.client.reqs.requests.post', side_effect=Exception("test error")) as mock_post:
        status, elapsed = reqs.send_270_request("http://example")
        assert status == -1
        assert elapsed >= 0
        mock_post.assert_called_once_with(url="http://example", data=reqs.samples.SAMPLE_270)