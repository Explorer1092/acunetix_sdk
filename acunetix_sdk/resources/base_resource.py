# Base class for API resources 
from typing import TypeVar, Generic, TYPE_CHECKING

# Use TYPE_CHECKING to guard imports for type hinting cycles
if TYPE_CHECKING:
    from ..client_base import BaseAcunetixClient # Generic client base
    # We don't strictly need Sync/AsyncHTTPClient here if TClient is well-defined
    # TClient will be BaseAcunetixClient[SyncHTTPClient] or BaseAcunetixClient[AsyncHTTPClient]

# Define TClient more broadly to be an instance of BaseAcunetixClient
# without specifying its generic http_client type here, as it creates circular dependencies
# with client_sync and client_async if we try to use their concrete types.
# Using a forward reference string for BaseAcunetixClient might be cleaner for TClient.
TClient = TypeVar("TClient", bound="BaseAcunetixClient")

class BaseResource(Generic[TClient]):
    """Base class for all API resource handlers (e.g., Targets, Scans)."""
    def __init__(self, client: TClient):
        """
        Initializes the resource with a client instance.
        :param client: An instance of AcunetixSyncClient or AcunetixAsyncClient.
        """
        self._client: TClient = client 