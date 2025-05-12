# tests/resources/test_targets_resource.py
import pytest
import pytest_asyncio
from unittest.mock import MagicMock, AsyncMock, patch

from acunetix_sdk import AcunetixSyncClient, AcunetixAsyncClient
from acunetix_sdk.resources.targets import TargetsSyncResource, TargetsAsyncResource
from acunetix_sdk.models.target import Target, TargetCreate, TargetUpdate, TargetBrief
from acunetix_sdk.models.pagination import PaginatedList, PaginationInfo
from acunetix_sdk.errors import AcunetixError, BadRequestError

API_KEY = "res_test_api_key"
ENDPOINT = "http://res-test.example.com"

# --- Synchronous Resource Fixtures & Tests ---
@pytest.fixture
def mock_sync_http_client_for_resource():
    client = MagicMock()
    client.request = MagicMock() # This is what BaseResource._client._request calls
    return client

@pytest.fixture
def targets_sync_resource(mock_sync_http_client_for_resource: MagicMock):
    # Create a dummy BaseAcunetixClient that uses the mocked http_client
    # The resource only needs the _request method from its parent client.
    parent_client = MagicMock()
    parent_client._request = mock_sync_http_client_for_resource.request 
    return TargetsSyncResource(parent_client)

class TestTargetsSyncResource:
    def test_list_targets_success(self, targets_sync_resource: TargetsSyncResource, mock_sync_http_client_for_resource: MagicMock):
        mock_api_response = {
            "targets": [{"target_id": "uuid1", "address": "http://example.com", "description": "Test", "type": "default", "criticality": 10}], # Changed items to targets and added missing fields for TargetResponse
            "pagination": {"next_cursor": "next_page_token", "count": 1, "total": 10}
        }
        mock_sync_http_client_for_resource.request.return_value = mock_api_response

        result = targets_sync_resource.list(limit=10, query="test")

        assert isinstance(result, PaginatedList)
        assert len(result.items) == 1
        assert isinstance(result.items[0], TargetResponse) # Changed TargetBrief to TargetResponse as list returns TargetResponse
        assert result.items[0].target_id == "uuid1"
        assert result.pagination.next_cursor == "next_page_token"
        mock_sync_http_client_for_resource.request.assert_called_once_with(
            "GET", "targets", params={"l": 10, "q": "test"} # cursor not passed initially
        )
    
    def test_create_target_success(self, targets_sync_resource: TargetsSyncResource, mock_sync_http_client_for_resource: MagicMock):
        create_payload = TargetCreate(address="http://new.example.com", description="New Target")
        mock_api_response = {"target_id": "new_uuid", **create_payload.model_dump(), "type": "default"}
        mock_sync_http_client_for_resource.request.return_value = mock_api_response

        result = targets_sync_resource.create(create_payload)

        assert isinstance(result, TargetResponse) # Changed from Target to TargetResponse
        assert result.target_id == "new_uuid"
        assert result.address == create_payload.address
        mock_sync_http_client_for_resource.request.assert_called_once_with(
            "POST", "targets", json_data=create_payload.model_dump(exclude_none=True)
        )

    def test_create_target_api_error(self, targets_sync_resource: TargetsSyncResource, mock_sync_http_client_for_resource: MagicMock):
        create_payload = TargetCreate(address="http://bad.example.com", description="Bad Target")
        # Simulate an API error by having the mocked request raise it
        mock_sync_http_client_for_resource.request.side_effect = BadRequestError("Invalid address", status_code=400)
        
        with pytest.raises(BadRequestError) as excinfo:
            targets_sync_resource.create(create_payload)
        assert excinfo.value.status_code == 400

    # ... Add tests for get, update, delete ...

# --- Asynchronous Resource Fixtures & Tests ---
@pytest_asyncio.fixture
async def mock_async_http_client_for_resource():
    client = MagicMock() # Using MagicMock because methods will be patched with AsyncMock
    client._arequest = AsyncMock() # This is what BaseResource._client._arequest calls
    return client

@pytest_asyncio.fixture
async def targets_async_resource(mock_async_http_client_for_resource: AsyncMock): # Changed parameter name
    parent_client = MagicMock() # Use AsyncMock if parent client has async methods used by resource
    parent_client._arequest = mock_async_http_client_for_resource._arequest # Changed variable name
    return TargetsAsyncResource(parent_client)

@pytest.mark.asyncio
class TestTargetsAsyncResource:
    async def test_list_targets_async_success(self, targets_async_resource: TargetsAsyncResource, mock_async_http_client_for_resource: AsyncMock):
        mock_api_response = {
            "targets": [{"target_id": "async_uuid1", "address": "http://async.example.com", "description": "Async Test", "type": "default", "criticality": 10}], # Changed items to targets and added missing fields
            "pagination": {"next_cursor": None, "count": 1, "total": 1} # Added count and total for pagination
        }
        # Configure the return value of the _arequest mock
        mock_async_http_client_for_resource._arequest.return_value = mock_api_response

        result = await targets_async_resource.list(limit=5)

        assert isinstance(result, PaginatedList)
        assert len(result.items) == 1
        assert isinstance(result.items[0], TargetResponse) # Changed TargetBrief to TargetResponse
        assert result.items[0].target_id == "async_uuid1"
        mock_async_http_client_for_resource._arequest.assert_called_once_with(
            "GET", "targets", params={"l": 5} # cursor not passed initially
        )
    
    # ... Add async tests for create, get, update, delete ...
