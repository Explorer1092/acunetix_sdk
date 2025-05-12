# tests/test_sync_client.py
import pytest
from unittest.mock import MagicMock, patch

from acunetix_sdk import AcunetixSyncClient, AcunetixError
from acunetix_sdk.http_clients import SyncHTTPClient
from acunetix_sdk.models.target import TargetBrief
from acunetix_sdk.models.pagination import PaginatedList, PaginationInfo

API_KEY = "test_sync_api_key"
ENDPOINT = "http://sync-test.example.com:1234"

@pytest.fixture
def mock_sync_http_client():
    mock = MagicMock(spec=SyncHTTPClient)
    mock.close = MagicMock() # Ensure close can be called
    return mock

@pytest.fixture
def sync_client(mock_sync_http_client: MagicMock):
    # Patch the SyncHTTPClient constructor within the scope of this fixture
    with patch('acunetix_sdk.client_sync.SyncHTTPClient', return_value=mock_sync_http_client) as PatchedClient:
        client = AcunetixSyncClient(api_key=API_KEY, endpoint=ENDPOINT, http_client=mock_sync_http_client)
        # Verify it used our mock if http_client was passed, or that constructor was called
        # If http_client is passed, constructor shouldn't be called again. 
        # If http_client is NOT passed, constructor *should* be called.
        # Let's test the case where we pass it for direct control.
        assert client.http_client is mock_sync_http_client 
        return client

class TestAcunetixSyncClient:
    def test_client_initialization(self):
        # Test initialization without passing an http_client, so it creates one
        with patch('acunetix_sdk.client_sync.SyncHTTPClient') as MockedInternalClientConst:
            internal_mock_instance = MockedInternalClientConst.return_value
            client = AcunetixSyncClient(api_key=API_KEY, endpoint=ENDPOINT, verify_ssl=False, timeout=45)
            MockedInternalClientConst.assert_called_once_with(verify_ssl=False)
            assert client.api_key == API_KEY
            assert client.base_url == f"https://{ENDPOINT.split('//')[-1]}/api/v1/"
            assert client.default_timeout == 45
            assert client.http_client is internal_mock_instance

    def test_client_context_manager(self, sync_client: AcunetixSyncClient, mock_sync_http_client: MagicMock):
        with sync_client as client_cm:
            assert client_cm is sync_client
        mock_sync_http_client.close.assert_called_once()

    def test_list_all_targets_pagination(self, sync_client: AcunetixSyncClient, mock_sync_http_client: MagicMock):
        # Mock the targets.list method which is called by list_all_targets
        # It should return PaginatedList[TargetBrief]
        mock_page1_data = {
            "items": [{"target_id": "t1", "address": "http://e1.com", "description": "d1"}],
            "pagination": {"next_cursor": "cursor2"}
        }
        mock_page2_data = {
            "items": [{"target_id": "t2", "address": "http://e2.com", "description": "d2"}],
            "pagination": {"next_cursor": None}
        }

        # list_method in _list_all_generic calls http_client.request
        # So we mock http_client.request directly which is what targets.list would resolve to
        # OR we can mock targets_resource.list if we don't want to go that deep.
        # Let's mock the resource's list method directly for this test.
        
        sync_client.targets.list = MagicMock()
        sync_client.targets.list.side_effect = [
            PaginatedList[TargetBrief](**mock_page1_data),
            PaginatedList[TargetBrief](**mock_page2_data)
        ]

        all_targets = list(sync_client.list_all_targets(page_limit=1))

        assert len(all_targets) == 2
        assert isinstance(all_targets[0], TargetBrief)
        assert all_targets[0].target_id == "t1"
        assert all_targets[1].target_id == "t2"

        # Check calls to the mocked targets.list
        assert sync_client.targets.list.call_count == 2
        sync_client.targets.list.assert_any_call(cursor=None, limit=1, query=None)
        sync_client.targets.list.assert_any_call(cursor="cursor2", limit=1, query=None)

    # Add more tests for other list_all_* methods and direct resource interactions. 