from typing import TYPE_CHECKING

from ..models.agent import AgentRegistrationToken, NewAgentRegistrationToken, AgentsConfig # Added AgentsConfig
from .base_resource import BaseResource
from ..errors import AcunetixError

if TYPE_CHECKING:
    from ..client_sync import AcunetixSyncClient
    from ..client_async import AcunetixAsyncClient

class AgentsConfigSyncResource(BaseResource["AcunetixSyncClient"]):
    """
    Handles synchronous operations related to Acunetix Agent registration configuration.
    Corresponds to endpoints under /config/agents.
    """

    def get_registration_token(self) -> AgentRegistrationToken:
        """
        Retrieves the current agent registration token.
        Corresponds to GET /config/agents/registration_token in API.
        API operationId: get_registration_token
        """
        response_data = self._client._request("GET", "config/agents/registration_token")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get registration token.")
        return AgentRegistrationToken(**response_data)

    def generate_registration_token(self, token_data: NewAgentRegistrationToken) -> AgentRegistrationToken:
        """
        Generates or regenerates an agent registration token.
        Corresponds to POST /config/agents/registration_token in API.
        API operationId: generate_registration_token
        """
        payload = token_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = self._client._request("POST", "config/agents/registration_token", json_data=payload)
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for generate registration token.")
        return AgentRegistrationToken(**response_data)

    def delete_registration_token(self) -> None:
        """
        Deletes the current agent registration token.
        Corresponds to DELETE /config/agents/registration_token in API.
        API operationId: remove_registration_token
        """
        self._client._request("DELETE", "config/agents/registration_token", expected_response_type="text")
        # API returns 204 No Content

    def get(self) -> AgentsConfig:
        """
        Retrieves the current agents configuration.
        Corresponds to GET /config/agents in API.
        """
        response_data = self._client._request("GET", "config/agents")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get agents configuration.")
        return AgentsConfig.model_validate(response_data)


class AgentsConfigAsyncResource(BaseResource["AcunetixAsyncClient"]):
    """
    Handles asynchronous operations related to Acunetix Agent registration configuration.
    """

    async def get_registration_token(self) -> AgentRegistrationToken:
        """Retrieves the current agent registration token asynchronously."""
        response_data = await self._client._arequest("GET", "config/agents/registration_token")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get registration token.")
        return AgentRegistrationToken(**response_data)

    async def generate_registration_token(self, token_data: NewAgentRegistrationToken) -> AgentRegistrationToken:
        """Generates or regenerates an agent registration token asynchronously."""
        payload = token_data.model_dump(exclude_none=True, by_alias=True, mode='json')
        response_data = await self._client._arequest("POST", "config/agents/registration_token", json_data=payload)
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for generate registration token.")
        return AgentRegistrationToken(**response_data)

    async def delete_registration_token(self) -> None:
        """Deletes the current agent registration token asynchronously."""
        await self._client._arequest("DELETE", "config/agents/registration_token", expected_response_type="text")

    async def get(self) -> AgentsConfig:
        """Retrieves the current agents configuration asynchronously."""
        response_data = await self._client._arequest("GET", "config/agents")
        if not isinstance(response_data, dict):
            raise AcunetixError("Unexpected response type for get agents configuration.")
        return AgentsConfig.model_validate(response_data)
