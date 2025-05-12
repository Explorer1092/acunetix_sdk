# HTTP client implementations 
import abc
import json as std_json # Alias to avoid confusion with method parameter
from typing import Any, Dict, Optional, Union, Literal
import logging # Added for logging errors
import urllib3 # Added for disabling InsecureRequestWarning

import requests
import httpx

from .errors import raise_for_status, AcunetixError

# logger = logging.getLogger(__name__) # Will use instance logger
ExpectedResponseType = Literal["json", "bytes", "text"]

class BaseHTTPClient(abc.ABC):
    """Abstract base class for HTTP clients."""

    def __init__(self, logger_instance: Optional[logging.Logger] = None):
        if logger_instance:
            self.logger = logger_instance
        else:
            self.logger = logging.getLogger("acunetix_sdk.http")
            if not self.logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
            if self.logger.level == logging.NOTSET: # Default to WARNING if not configured
                self.logger.setLevel(logging.WARNING)

    def _handle_response_content(
        self,
        response: Union[requests.Response, httpx.Response],
        expected_type: ExpectedResponseType = "json"
    ) -> Union[Dict[str, Any], bytes, str]:
        """Handles response status, raises errors, and parses content based on expected_type."""
        status_code = response.status_code
        response_text = ""
        try:
            # Eagerly read content to avoid issues with streaming/consumption
            response_content = response.content
            # Attempt to decode as text for error messages, ignore if fails
            try:
                response_text = response_content.decode('utf-8')
            except UnicodeDecodeError:
                response_text = "[non-utf8 binary content]"
        except Exception as e:
             # Handle cases where .content might fail on some stream responses before full read
             self.logger.warning(f"Could not read response content for status {status_code}: {e}")
             response_content = b'' # Ensure content is bytes
             response_text = "[failed to read response content]"
        
        # Check for errors first
        if not (200 <= status_code < 300):
            # Pass the read text to the error handler
            raise_for_status(status_code, response_text)

        # Handle successful responses
        if status_code == 204:  # No Content
            if expected_type == "json": return {}
            if expected_type == "bytes": return b''
            return ""

        if expected_type == "bytes":
            return response_content # Return the raw bytes read earlier
        
        # response_text should be populated from earlier try/except
        if expected_type == "text":
            return response_text

        # Default to JSON parsing
        if not response_text.strip(): 
            return {}
        
        try:
            # Use std_json.loads on the text we already decoded
            return std_json.loads(response_text)
        except std_json.JSONDecodeError as e:
            self.logger.error(f"JSON decode failed for status {status_code}. Response text: {response_text[:500]}...") # Log snippet
            raise AcunetixError(
                message=f"Failed to decode JSON response.",
                status_code=status_code,
                response_text=response_text
            ) from e

    @abc.abstractmethod
    def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_payload: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        timeout: Optional[int] = 30,
        expected_response_type: ExpectedResponseType = "json",
        return_raw_response: bool = False, # Added for client_base
    ) -> Union[Dict[str, Any], bytes, str, Any]: # Adjusted for client_base
        pass


class SyncHTTPClient(BaseHTTPClient):
    """Synchronous HTTP client using requests."""
    def __init__(self, verify_ssl: bool = False, logger_instance: Optional[logging.Logger] = None):
        super().__init__(logger_instance=logger_instance)
        self.session = requests.Session()
        self.session.verify = verify_ssl
        if not verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_payload: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        timeout: Optional[int] = 30,
        expected_response_type: ExpectedResponseType = "json",
        return_raw_response: bool = False, # Added for client_base
    ) -> Union[Dict[str, Any], bytes, str, Any]: # Adjusted for client_base
        # Ensure 'Accept' header matches if expecting JSON, allow override for other types
        req_headers = headers.copy() if headers else {}
        if expected_response_type == "json" and "Accept" not in req_headers:
            req_headers["Accept"] = "application/json"
        elif expected_response_type == "bytes" and "Accept" not in req_headers:
            req_headers["Accept"] = "application/octet-stream" # Common for byte streams

        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                headers=req_headers,
                params=params,
                json=json_payload,
                data=data,
                timeout=timeout,
                # stream=(expected_response_type == "bytes") # Not strictly needed for requests
            )
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug(f"HTTP Response Status: {response.status_code} for {response.url}")
                self.logger.debug(f"HTTP Response Headers: {dict(response.headers)}")

            if return_raw_response: # Used by BaseAcunetixClient for its own logging if needed
                return response

        except requests.exceptions.Timeout as e:
            self.logger.error(f"Request timed out to {url}: {e}")
            raise AcunetixError(f"Request timed out to {url}") from e
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error to {url}: {e}")
            raise AcunetixError(f"Connection error to {url}") from e
        except requests.exceptions.RequestException as e:
            self.logger.error(f"An unexpected error occurred during the request to {url}: {e}")
            raise AcunetixError(f"An unexpected error occurred during the request to {url}: {e}") from e
        
        return self._handle_response_content(response, expected_response_type)

    def close(self):
        """Closes the underlying requests session."""
        self.session.close()


class AsyncHTTPClient(BaseHTTPClient):
    """Asynchronous HTTP client using httpx."""
    def __init__(self, verify_ssl: bool = False, logger_instance: Optional[logging.Logger] = None):
        super().__init__(logger_instance=logger_instance)
        # Consider http2 support? httpx.AsyncClient(http2=True, ...) if API supports it.
        self._client = httpx.AsyncClient(verify=verify_ssl)

    async def request(  # This method is async
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_payload: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        timeout: Optional[int] = 30,
        expected_response_type: ExpectedResponseType = "json",
        return_raw_response: bool = False, # Added for client_base
    ) -> Union[Dict[str, Any], bytes, str, Any]: # Adjusted for client_base
        req_headers = headers.copy() if headers else {}
        if expected_response_type == "json" and "Accept" not in req_headers:
            req_headers["Accept"] = "application/json"
        elif expected_response_type == "bytes" and "Accept" not in req_headers:
            req_headers["Accept"] = "application/octet-stream"

        try:
            response = await self._client.request(
                method=method.upper(),
                url=url,
                headers=req_headers,
                params=params,
                json=json_payload,
                content=data, 
                timeout=timeout,
            )
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug(f"HTTP Response Status: {response.status_code} for {response.url}")
                self.logger.debug(f"HTTP Response Headers: {dict(response.headers)}")

            if return_raw_response: # Used by BaseAcunetixClient for its own logging if needed
                return response
                
        except httpx.TimeoutException as e:
            self.logger.error(f"Request timed out to {url}: {e}")
            raise AcunetixError(f"Request timed out to {url}") from e
        except httpx.ConnectError as e:
            self.logger.error(f"Connection error to {url}: {e}")
            raise AcunetixError(f"Connection error to {url}") from e
        except httpx.HTTPError as e: 
            self.logger.error(f"An unexpected HTTP error occurred for {url}: {e}")
            raise AcunetixError(f"An unexpected HTTP error occurred for {url}: {e}") from e

        return self._handle_response_content(response, expected_response_type)

    async def close(self):
        """Closes the underlying httpx client."""
        await self._client.aclose()
