from typing import Optional, TYPE_CHECKING

from ..models.worker import (
    WorkerList,
    Worker,
    WorkerExtended,
    WorkerDescription,
    EmptyObject # For requests with empty body
)
# Pagination is not specified for GET /workers.
from .base_resource import BaseResource
from ..errors import AcunetixError

if TYPE_CHECKING:
    from ..client_sync import AcunetixSyncClient
    from ..client_async import AcunetixAsyncClient

class WorkersSyncResource(BaseResource["AcunetixSyncClient"]):
    """Handles synchronous operations related to Acunetix Workers."""

    def list(self) -> WorkerList:
        """
        Lists all registered workers.
        Corresponds to GET /workers in API.
        API operationId: get_workers
        """
        response_data = self._client._request("GET", "workers")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for list workers.")
        return WorkerList(**response_data)

    def get(self, worker_id: str) -> Worker:
        """
        Retrieves a specific worker by ID.
        Corresponds to GET /workers/{worker_id} in API.
        API operationId: get_worker
        """
        response_data = self._client._request("GET", f"workers/{worker_id}")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get worker.")
        return Worker(**response_data)

    def delete(self, worker_id: str) -> None: # API returns 204
        """
        Deletes a specific worker.
        Corresponds to DELETE /workers/{worker_id} in API.
        API operationId: delete_worker
        """
        self._client._request("DELETE", f"workers/{worker_id}")

    def ignore_errors(self, worker_id: str) -> None: # API returns 204
        """
        Ignores errors for a specific worker.
        Corresponds to DELETE /workers/{worker_id}/ignore_errors in API.
        API operationId: delete_worker_ignore_errors
        """
        self._client._request("DELETE", f"workers/{worker_id}/ignore_errors")

    def authorize(self, worker_id: str) -> None: # API returns 204
        """
        Authorizes a specific worker.
        Corresponds to POST /workers/{worker_id}/authorize in API.
        API operationId: authorize_worker
        """
        self._client._request("POST", f"workers/{worker_id}/authorize", json_data=EmptyObject().model_dump(exclude_none=True, by_alias=True, mode='json'))

    def deauthorize(self, worker_id: str) -> None: # API returns 204
        """
        取消授权一个特定的工作器。
        对应API中的 POST /workers/{worker_id}/reject 端点。
        实际上是通过 reject 端点实现的，因为API没有专门的取消授权端点。
        """
        self._client._request("POST", f"workers/{worker_id}/reject", json_data=EmptyObject().model_dump(exclude_none=True, by_alias=True, mode='json'))

    def reject(self, worker_id: str) -> None: # API returns 204
        """
        Rejects a specific worker.
        Corresponds to POST /workers/{worker_id}/reject in API.
        API operationId: reject_worker
        """
        self._client._request("POST", f"workers/{worker_id}/reject", json_data=EmptyObject().model_dump(exclude_none=True, by_alias=True, mode='json'))

    def check_connection(self, worker_id: str) -> WorkerExtended:
        """
        Checks a specific worker's connection.
        Corresponds to POST /workers/{worker_id}/check in API.
        API operationId: check_worker
        """
        response_data = self._client._request("POST", f"workers/{worker_id}/check", json_data=EmptyObject().model_dump(exclude_none=True, by_alias=True, mode='json'))
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for check worker connection.")
        return WorkerExtended(**response_data)

    def upgrade(self, worker_id: str) -> None: # API returns 204
        """
        Upgrades a specific worker.
        Corresponds to POST /workers/{worker_id}/upgrade in API.
        API operationId: upgrade_worker
        """
        self._client._request("POST", f"workers/{worker_id}/upgrade", json_data=EmptyObject().model_dump(exclude_none=True, by_alias=True, mode='json'))

    def rename(self, worker_id: str, description_data: WorkerDescription) -> None: # API returns 204
        """
        Renames a specific worker.
        Corresponds to POST /workers/{worker_id}/rename in API.
        API operationId: rename_worker
        """
        payload = description_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        self._client._request("POST", f"workers/{worker_id}/rename", json_data=payload)


class WorkersAsyncResource(BaseResource["AcunetixAsyncClient"]):
    """Handles asynchronous operations related to Acunetix Workers."""

    async def list(self) -> WorkerList:
        response_data = await self._client._arequest("GET", "workers")
        if not isinstance(response_data, dict):
            raise AcunetixError("Async: Unexpected response for list workers.")
        return WorkerList(**response_data)

    async def get(self, worker_id: str) -> Worker:
        response_data = await self._client._arequest("GET", f"workers/{worker_id}")
        if not isinstance(response_data, dict):
            raise AcunetixError("Async: Unexpected response for get worker.")
        return Worker(**response_data)

    async def delete(self, worker_id: str) -> None:
        await self._client._arequest("DELETE", f"workers/{worker_id}")

    async def ignore_errors(self, worker_id: str) -> None:
        await self._client._arequest("DELETE", f"workers/{worker_id}/ignore_errors")

    async def authorize(self, worker_id: str) -> None:
        await self._client._arequest("POST", f"workers/{worker_id}/authorize", json_data=EmptyObject().model_dump(exclude_none=True, by_alias=True, mode='json'))

    async def deauthorize(self, worker_id: str) -> None:
        """
        异步取消授权一个特定的工作器。
        通过 reject 端点实现，因为API没有专门的取消授权端点。
        """
        await self._client._arequest("POST", f"workers/{worker_id}/reject", json_data=EmptyObject().model_dump(exclude_none=True, by_alias=True, mode='json'))

    async def reject(self, worker_id: str) -> None:
        await self._client._arequest("POST", f"workers/{worker_id}/reject", json_data=EmptyObject().model_dump(exclude_none=True, by_alias=True, mode='json'))

    async def check_connection(self, worker_id: str) -> WorkerExtended:
        response_data = await self._client._arequest("POST", f"workers/{worker_id}/check", json_data=EmptyObject().model_dump(exclude_none=True, by_alias=True, mode='json'))
        if not isinstance(response_data, dict):
            raise AcunetixError("Async: Unexpected response for check worker connection.")
        return WorkerExtended(**response_data)

    async def upgrade(self, worker_id: str) -> None:
        await self._client._arequest("POST", f"workers/{worker_id}/upgrade", json_data=EmptyObject().model_dump(exclude_none=True, by_alias=True, mode='json'))

    async def rename(self, worker_id: str, description_data: WorkerDescription) -> None:
        payload = description_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        await self._client._arequest("POST", f"workers/{worker_id}/rename", json_data=payload)
