# Acunetix Python SDK

[![PyPI version](https://badge.fury.io/py/acunetix-sdk.svg)](https://badge.fury.io/py/acunetix-sdk) <!-- Placeholder, update if publishing -->
<!-- [![Build Status](https://travis-ci.org/yourusername/acunetix-sdk.svg?branch=main)](https://travis-ci.org/yourusername/acunetix-sdk) -->
<!-- [![Coverage Status](https://coveralls.io/repos/github/yourusername/acunetix-sdk/badge.svg?branch=main)](https://coveralls.io/github/yourusername/acunetix-sdk?branch=main) -->

A Python client for the Acunetix API, providing both synchronous and asynchronous interfaces for interacting with Acunetix vulnerability scanning services.

## Features

*   Support for major Acunetix API resources (Targets, Scans, Reports, Users, Scan Profiles, Report Templates, Notifications - _verification against official docs pending_).
*   Both synchronous (`AcunetixSyncClient`) and asynchronous (`AcunetixAsyncClient`) clients.
*   Context manager support for automatic client resource cleanup.
*   Pydantic models for API request/response validation and type-safe data handling.
*   Helper methods for easy pagination through resource lists.
*   Polling helpers in the async client for long-running operations like scan/report completion.
*   Extensible HTTP client layer, allowing injection of custom pre-configured clients.
*   Basic logging integration.
*   **Command Line Interface** - 包含功能齐全的命令行工具，用于管理目标、扫描、报告和其他 Acunetix 资源。

## Installation

```bash
pip install acunetix-sdk
```

Or, if you have cloned the repository:

```bash
poetry install
```

## Usage

### Synchronous Client

```python
from acunetix_sdk import AcunetixSyncClient, AcunetixError, TargetBrief, TargetCreate
from pydantic import HttpUrl # For creating HttpUrl instances

# Replace with your actual API key and endpoint
API_KEY = "YOUR_ACUNETIX_API_KEY"
ENDPOINT = "your-acunetix-instance.com:3443"

# Using the client with a context manager is recommended
with AcunetixSyncClient(api_key=API_KEY, endpoint=ENDPOINT) as client:
    try:
        print("Fetching first 2 targets...")
        for target in client.list_all_targets(page_limit=2):
            print(f"  ID: {target.target_id}, Address: {target.address}, Description: {target.description}")
        
        # Example: Create a new target
        # new_target_payload = TargetCreate(
        #     address=HttpUrl("http://testphp.vulnweb.com"), 
        #     description="My Test Target (Sync)"
        # )
        # created_target = client.targets.create(new_target_payload)
        # print(f"\nCreated Target: {created_target.target_id} - {created_target.address}")
        # client.targets.delete(created_target.target_id) # Cleanup
        # print(f"Deleted target {created_target.target_id}")

    except AcunetixError as e:
        print(f"An API error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
# client.close() is automatically called by the context manager
```

### Asynchronous Client

```python
import asyncio
import logging
from acunetix_sdk import AcunetixAsyncClient, AcunetixError, TargetBrief, Scan, ReportStatus
from acunetix_sdk.models.scan import ScanCreate # If needed for specific creation payload
from acunetix_sdk.models.report import ReportCreate, ReportSource # If needed
from pydantic import HttpUrl

API_KEY = "YOUR_ACUNETIX_API_KEY"
ENDPOINT = "your-acunetix-instance.com:3443"

# Basic logging setup to see SDK debug messages and polling info
logging.basicConfig(level=logging.INFO)
logging.getLogger("acunetix_sdk").setLevel(logging.DEBUG) # More verbose for SDK specific logs

async def main():
    # Using the async client with a context manager
    async with AcunetixAsyncClient(api_key=API_KEY, endpoint=ENDPOINT) as client:
        try:
            print("Fetching first 2 targets asynchronously...")
            async for target in client.list_all_targets(page_limit=2):
                print(f"  ID: {target.target_id}, Address: {target.address}")

            # Example: Start a scan and wait for completion (replace with valid IDs)
            # target_to_scan_id = "<your_target_id>" 
            # profile_to_use_id = "<your_scan_profile_id>"
            # if target_to_scan_id and profile_to_use_id:
            #     print(f"\nStarting scan on target {target_to_scan_id}...")
            #     scan_payload = ScanCreate(target_id=target_to_scan_id, profile_id=profile_to_use_id)
            #     started_scan = await client.scans.create(scan_payload)
            #     print(f"Scan {started_scan.scan_id} started with status: {started_scan.status}")
            #     
            #     completed_scan = await client.wait_for_scan_completion(started_scan.scan_id, poll_interval=10, timeout=1800)
            #     print(f"Scan {completed_scan.scan_id} finished with status: {completed_scan.status}")
            # 
            #     if completed_scan.status.lower() == "completed":
            #         print("Generating report for completed scan...")
            #         report_payload = ReportCreate(
            #             template_id="<your_report_template_id>", # e.g., Developer template ID
            #             source=ReportSource(list_type="scans", id_list=[completed_scan.scan_id])
            #         )
            #         created_report_info = await client.reports.create(report_payload)
            #         print(f"Report {created_report_info.report_id} requested with status: {created_report_info.status}")
            #         
            #         final_report_info = await client.wait_for_report_completion(created_report_info.report_id, poll_interval=5, timeout=300)
            #         print(f"Report {final_report_info.report_id} generation finished with status: {final_report_info.status}")
            #         if final_report_info.status == ReportStatus.COMPLETED and final_report_info.download_link:
            #             print(f"Report download link (example, actual download needs specific handling): {final_report_info.download_link}")
            #             # report_bytes_io = await client.reports.download(final_report_info.report_id) # Assuming PDF by default
            #             # with open(f"{final_report_info.report_id}.pdf", "wb") as f:
            #             #     f.write(report_bytes_io.read())
            #             # print(f"Report downloaded to {final_report_info.report_id}.pdf")

        except AcunetixError as e:
            print(f"An API error occurred: {e}")
            if e.response_text:
                print(f"Response body: {e.response_text}")
        except TimeoutError as e:
            print(f"An operation timed out: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    # await client.close() is automatically called by the async context manager

if __name__ == "__main__":
    asyncio.run(main())
```

## Logging

The SDK uses Python's standard `logging` module. You can configure it as part of your application's logging setup to control the verbosity of SDK messages. The primary loggers used within the SDK are typically under the `acunetix_sdk` namespace (e.g., `acunetix_sdk.client_base`, `acunetix_sdk.http_clients`, `acunetix_sdk.client_async` for polling).

**Basic Configuration Example:**

```python
import logging

# Show all DEBUG level messages from all loggers
# logging.basicConfig(level=logging.DEBUG)

# More targeted: Show INFO for application, DEBUG for SDK components
logging.basicConfig(level=logging.INFO) # Your app's default level
logging.getLogger("acunetix_sdk").setLevel(logging.DEBUG)

# Example: To see detailed HTTP request/response information (if http_clients adds it)
# logging.getLogger("acunetix_sdk.http_clients").setLevel(logging.DEBUG)

# Example: To see async polling status updates
# logging.getLogger("acunetix_sdk.client_async").setLevel(logging.DEBUG)
```

## Development

This project uses [Poetry](https://python-poetry.org/) for dependency management and packaging.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Explorer1092/acunetix_sdk.git # Update with actual repo URL
    cd acunetix_sdk
    ```

2.  **Install dependencies:**
    ```bash
    poetry install
    ```

3.  **Activate the virtual environment:**
    ```bash
    poetry shell
    ```

4.  **Run linters/formatters (configured in `pyproject.toml`):**
    ```bash
    black .
    isort .
    flake8 .
    mypy src/
    ```

5.  **Run tests (TODO: Implement tests):**
    ```bash
    pytest
    ```

## TODO / Remaining Work

*   **Crucial: Full API Documentation Alignment:** Verify all models, endpoint paths, parameters, and response structures against official Acunetix API documentation.
*   **Expand Unit & Integration Tests:** Increase coverage for edge-cases and error paths.
*   **Webhook Support Investigation:** If Acunetix API supports webhooks for asynchronous events, consider adding utilities for their consumption.
*   **Advanced Error Handling:** Map specific Acunetix error codes (if available beyond HTTP status) to more granular exceptions or include more detail in existing ones.
*   **Full Documentation:** Complete all docstrings and generate API reference documentation.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an Issue.

## License

This SDK is distributed under the MIT License. See `LICENSE` for more information. 

## 文档

- [AWVS CLI 使用指南](docs/awvs_cli_usage.md) - 命令行工具详细使用方法
- [API 参考文档](https://explorer1092.github.io/acunetix_sdk/api-reference.html) - 完整 API 参考 (在线)

> **在线文档**: https://explorer1092.github.io/acunetix_sdk/ 