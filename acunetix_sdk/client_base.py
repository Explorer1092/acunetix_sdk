# Base Acunetix client logic 
from typing import Any, Dict, Optional, TypeVar, Generic, Coroutine, Union
from urllib.parse import urljoin
import logging
import json # 导入 json 模块

from .http_clients import BaseHTTPClient, SyncHTTPClient, AsyncHTTPClient, ExpectedResponseType
from .errors import AcunetixError # Assuming AcunetixError is defined in .errors

# For generic typing of the HTTP client used by BaseAcunetixClient
T_HttpClient = TypeVar("T_HttpClient", bound=BaseHTTPClient)

# SDK_LOGGER_NAME = "acunetix_sdk" # Use this if creating a specific SDK logger

class BaseAcunetixClient(Generic[T_HttpClient]):
    """Base class for Acunetix API clients, handling common logic."""
    def __init__(
        self,
        api_key: str,
        endpoint: str, # e.g., "acunetix.example.com:3443" or just "acunetix.example.com"
        http_client: T_HttpClient,
        default_timeout: Optional[int] = 30, # Default timeout for requests in seconds
        logger: Optional[logging.Logger] = None, # Added logger parameter
    ):
        if not api_key:
            raise ValueError("API key cannot be empty.")
        if not endpoint:
            raise ValueError("Endpoint cannot be empty.")

        # Initialize logger
        if logger: # If a logger instance is provided (e.g., pre-configured by CLI)
            self.logger = logger
        else: # Otherwise, setup a default logger for the SDK
            self.logger = logging.getLogger("acunetix_sdk")
            if not self.logger.handlers: # Only add a handler if no handlers are already configured
                handler = logging.StreamHandler()
                formatter = logging.Formatter('%(asctime)s - %(name)s (SDK-default) - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
                # Set a default level for the logger only if we added the handler AND its level is not already set
                if self.logger.level == logging.NOTSET:
                    self.logger.setLevel(logging.WARNING)
            elif self.logger.level == logging.NOTSET: # If handlers exist but logger level is not set
                # This case might occur if root logger has handlers but "acunetix_sdk" logger itself doesn't have a level
                self.logger.setLevel(logging.WARNING) # Default to WARNING

        self.api_key = api_key
        # Ensure endpoint is just the host:port or host, then construct base_url
        if "://" in endpoint:
            _, remainder = endpoint.split("://", 1)
            host_port = remainder.split('/', 1)[0] if '/' in remainder else remainder
        elif '/' in endpoint: # if someone passes endpoint/api/v1
             host_port, _ = endpoint.split('/',1)
        else:
            host_port = endpoint
        
        self.base_url = f"https://{host_port.strip('/')}/api/v1/" # Ensure trailing slash
        
        # If http_client is an instance (passed in), it should already have its logger.
        # If http_client is a class type to be instantiated here (not current design but for future),
        # then self.logger should be passed to its constructor.
        # Current design: http_client is always an instance passed from AcunetixSyncClient/AcunetixAsyncClient
        self.http_client: T_HttpClient = http_client
        
        self.default_timeout = default_timeout
        self.logger.debug(f"BaseAcunetixClient initialized with base URL: {self.base_url}")

    def _prepare_url(self, path: str) -> str:
        """Constructs the full URL for an API request."""
        # path.lstrip('/') ensures no double slashes if path starts with /
        full_url = urljoin(self.base_url, path.lstrip('/'))
        # self.logger.debug(f"Prepared URL: {full_url}") # URL logging will be part of request details
        return full_url

    def _prepare_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Prepares standard request headers including authentication."""
        headers = {
            "X-Auth": self.api_key,
            # "Content-Type": "application/json", # Content-Type is often set by requests/httpx based on json/data
        }
        # Ensure Content-Type is application/json if json_data is used, unless overridden
        # This logic might be better placed where json_data is known.
        # For now, let http_clients handle default Content-Type if json_payload is passed.

        if additional_headers:
            headers.update(additional_headers)
        return headers

    def _request( # For synchronous client
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        timeout: Optional[int] = None,
        expected_response_type: ExpectedResponseType = "json",
        additional_headers: Optional[Dict[str, str]] = None,
        # return_raw_response: bool = False, # Removed, http_client handles its logging
    ) -> Union[Dict[str, Any], bytes, str]: 
        """Makes a synchronous API request."""
        if not isinstance(self.http_client, SyncHTTPClient):
            raise TypeError("SyncHTTPClient required for _request. Use _arequest for async.")
        
        url = self._prepare_url(path)
        headers = self._prepare_headers(additional_headers)
        # Add Content-Type if json_data is present and not already in headers
        if json_data is not None and "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        request_timeout = timeout if timeout is not None else self.default_timeout
        
        if self.logger.isEnabledFor(logging.DEBUG):
            log_msg_parts = [
                f"Sync Request:",
                f"  Method: {method.upper()}",
                f"  URL: {url}",
                f"  Headers: {headers}",
            ]
            if params:
                log_msg_parts.append(f"  Params: {params}")
            if json_data:
                try:
                    log_msg_parts.append(f"  JSON Body: {json.dumps(json_data, indent=2)}")
                except TypeError: # pragma: no cover
                    log_msg_parts.append(f"  JSON Body (unserializable): {json_data}")
            elif data:
                if isinstance(data, (str, bytes)):
                    log_msg_parts.append(f"  Data Body (first 200 chars): {str(data)[:200]}")
                else:
                    log_msg_parts.append(f"  Data Body Type: {type(data)}")
            log_msg_parts.append(f"  Timeout: {request_timeout}")
            log_msg_parts.append(f"  Expected Response: {expected_response_type}")
            self.logger.debug("\n".join(log_msg_parts))
        
        response_content = self.http_client.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json_payload=json_data,
            data=data,
            timeout=request_timeout,
            expected_response_type=expected_response_type
            # return_raw_response=False # No longer needed here
        )

        if self.logger.isEnabledFor(logging.DEBUG):
            log_resp_msg = f"Sync Response Body (type: {expected_response_type}):\n"
            if expected_response_type == "json" and isinstance(response_content, dict):
                try:
                    log_resp_msg += f"{json.dumps(response_content, indent=2, ensure_ascii=False)}"
                except TypeError: # pragma: no cover
                    log_resp_msg += f"{response_content}"
            elif isinstance(response_content, str):
                log_resp_msg += f"{response_content[:1000]}" # Truncate long strings
                if len(response_content) > 1000: log_resp_msg += "..."
            elif isinstance(response_content, bytes):
                log_resp_msg += f"Bytes response, length: {len(response_content)}. First 200 bytes: {response_content[:200]}"
                if len(response_content) > 200: log_resp_msg += b"..."
            else: # pragma: no cover
                log_resp_msg += f"{response_content}"
            self.logger.debug(log_resp_msg)
            
        return response_content

    async def _arequest( # For asynchronous client
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        timeout: Optional[int] = None,
        expected_response_type: ExpectedResponseType = "json",
        additional_headers: Optional[Dict[str, str]] = None,
        # return_raw_response: bool = False, # Removed
    ) -> Union[Dict[str, Any], bytes, str]:
        """Makes an asynchronous API request."""
        if not isinstance(self.http_client, AsyncHTTPClient):
            raise TypeError("AsyncHTTPClient required for _arequest.")
        
        url = self._prepare_url(path)
        headers = self._prepare_headers(additional_headers)
        if json_data is not None and "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"
            
        request_timeout = timeout if timeout is not None else self.default_timeout

        if self.logger.isEnabledFor(logging.DEBUG):
            log_msg_parts = [
                f"Async Request:",
                f"  Method: {method.upper()}",
                f"  URL: {url}",
                f"  Headers: {headers}",
            ]
            if params:
                log_msg_parts.append(f"  Params: {params}")
            if json_data:
                try:
                    log_msg_parts.append(f"  JSON Body: {json.dumps(json_data, indent=2)}")
                except TypeError: # pragma: no cover
                    log_msg_parts.append(f"  JSON Body (unserializable): {json_data}")
            elif data:
                if isinstance(data, (str, bytes)):
                    log_msg_parts.append(f"  Data Body (first 200 chars): {str(data)[:200]}")
                else:
                    log_msg_parts.append(f"  Data Body Type: {type(data)}")
            log_msg_parts.append(f"  Timeout: {request_timeout}")
            log_msg_parts.append(f"  Expected Response: {expected_response_type}")
            self.logger.debug("\n".join(log_msg_parts))

        response_content = await self.http_client.request( # type: ignore
            method=method,
            url=url,
            headers=headers,
            params=params,
            json_payload=json_data,
            data=data,
            timeout=request_timeout,
            expected_response_type=expected_response_type
            # return_raw_response=False # No longer needed here
        )

        if self.logger.isEnabledFor(logging.DEBUG):
            log_resp_msg = f"Async Response Body (type: {expected_response_type}):\n"
            if expected_response_type == "json" and isinstance(response_content, dict):
                try:
                    log_resp_msg += f"{json.dumps(response_content, indent=2, ensure_ascii=False)}"
                except TypeError: # pragma: no cover
                    log_resp_msg += f"{response_content}"
            elif isinstance(response_content, str):
                log_resp_msg += f"{response_content[:1000]}"
                if len(response_content) > 1000: log_resp_msg += "..."
            elif isinstance(response_content, bytes):
                log_resp_msg += f"Bytes response, length: {len(response_content)}. First 200 bytes: {response_content[:200]}"
                if len(response_content) > 200: log_resp_msg += b"..."
            else: # pragma: no cover
                log_resp_msg += f"{response_content}"
            self.logger.debug(log_resp_msg)
            
        return response_content
