# tests/test_async_client.py
import pytest
import pytest_asyncio # For async fixtures
from unittest.mock import MagicMock, patch, AsyncMock

from acunetix_sdk import AcunetixAsyncClient, AcunetixError
from acunetix_sdk.http_clients import AsyncHTTPClient
from acunetix_sdk.models.target import TargetBrief
from acunetix_sdk.models.scan import Scan
from acunetix_sdk.models.pagination import PaginatedList, PaginationInfo

API_KEY = "test_async_api_key"
ENDPOINT = "http://async-test.example.com:1234"

@pytest_asyncio.fixture
async def mock_async_http_client():
    # AsyncMock is preferred for async methods
    mock = AsyncMock(spec=AsyncHTTPClient)
    mock.close = AsyncMock() # Ensure close is awaitable
    # Mock the request method to be an awaitable function
    mock.request = AsyncMock(return_value={"items": [], "pagination": {"next_cursor": None}})
    return mock

@pytest_asyncio.fixture
async def async_client(mock_async_http_client: AsyncMock):
    with patch('acunetix_sdk.client_async.AsyncHTTPClient', return_value=mock_async_http_client):
        client = AcunetixAsyncClient(api_key=API_KEY, endpoint=ENDPOINT, http_client=mock_async_http_client)
        assert client.http_client is mock_async_http_client
        yield client # Use yield for async fixtures that need cleanup if client had explicit start
        # No explicit start for this client, but good practice for async fixtures
        # await client.close() # Client itself should be closed by test if not using context manager

@pytest.mark.asyncio
class TestAcunetixAsyncClient:
    async def test_client_initialization(self):
        with patch('acunetix_sdk.client_async.AsyncHTTPClient') as MockedInternalClientConst:
            internal_mock_instance = MockedInternalClientConst.return_value
            internal_mock_instance.close = AsyncMock() # ensure it has an async close
            
            client = AcunetixAsyncClient(api_key=API_KEY, endpoint=ENDPOINT, verify_ssl=False, timeout=25)
            MockedInternalClientConst.assert_called_once_with(verify_ssl=False)
            assert client.api_key == API_KEY
            assert client.default_timeout == 25
            assert client.http_client is internal_mock_instance
            await client.close() # Important to close the internally created client

    async def test_client_context_manager(self, async_client: AcunetixAsyncClient, mock_async_http_client: AsyncMock):
        async with async_client as client_cm:
            assert client_cm is async_client
        mock_async_http_client.close.assert_called_once()

    async def test_list_all_targets_async_pagination(self, async_client: AcunetixAsyncClient):
        mock_page1_data = {
            "items": [{"target_id": "t1", "address": "http://e1.com", "description": "d1"}],
            "pagination": {"next_cursor": "cursor2"}
        }
        mock_page2_data = {
            "items": [{"target_id": "t2", "address": "http://e2.com", "description": "d2"}],
            "pagination": {"next_cursor": None}
        }
        
        async_client.targets.list = AsyncMock()
        async_client.targets.list.side_effect = [
            PaginatedList[TargetBrief](**mock_page1_data),
            PaginatedList[TargetBrief](**mock_page2_data)
        ]

        all_targets = []
        async for target in async_client.list_all_targets(page_limit=1):
            all_targets.append(target)

        assert len(all_targets) == 2
        assert isinstance(all_targets[0], TargetBrief)
        assert all_targets[0].target_id == "t1"

        assert async_client.targets.list.call_count == 2
        async_client.targets.list.assert_any_call(cursor=None, limit=1, query=None, sort=None) # Added sort=None
        async_client.targets.list.assert_any_call(cursor="cursor2", limit=1, query=None, sort=None) # Added sort=None

    async def test_wait_for_scan_completion(self, async_client: AcunetixAsyncClient):
        scan_id = "test-scan-id"
        final_scan_data = {"scan_id": scan_id, "target_id": "t1", "profile_id": "p1", "status": "completed"}
        
        # Mock the scans.get method
        async_client.scans.get = AsyncMock()
        
        # Create valid UUIDs for IDs
        valid_scan_id = "00000000-0000-0000-0000-000000000000" # Placeholder UUID
        valid_target_id = "11111111-1111-1111-1111-111111111111" # Placeholder UUID
        valid_profile_id = "22222222-2222-2222-2222-222222222222" # Placeholder UUID
        
        # Minimal valid schedule
        mock_schedule = {"disable": False, "start_date": None, "recurrence": None, "time_sensitive": False, "history_limit": 0, "triggerable": False}

        final_scan_data_complete = {
            "scan_id": valid_scan_id, 
            "target_id": valid_target_id, 
            "profile_id": valid_profile_id, 
            "status": "completed", # This should come from ScanInfo within current_session
            "schedule": mock_schedule,
            "current_session": {"status": "completed"} # Simplified current_session
        }


        async_client.scans.get.side_effect = [
            Scan(scan_id=valid_scan_id, target_id=valid_target_id, profile_id=valid_profile_id, schedule=mock_schedule, current_session={"status": "processing"}),
            Scan(scan_id=valid_scan_id, target_id=valid_target_id, profile_id=valid_profile_id, schedule=mock_schedule, current_session={"status": "processing"}),
            Scan(**final_scan_data_complete)
        ]

        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            completed_scan = await async_client.wait_for_scan_completion(scan_id, poll_interval=0.01)
        
        assert isinstance(completed_scan, Scan)
        assert completed_scan.current_session.status == "completed" # Check status within current_session
        assert async_client.scans.get.call_count == 3
        assert mock_sleep.call_count == 2 # Called before each retry that isn't terminal

    # Add more tests for other list_all_*, wait_for_*, and direct resource interactions.
