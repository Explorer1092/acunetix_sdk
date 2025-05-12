# tests/test_models.py
import pytest
from pydantic import ValidationError
import datetime

from acunetix_sdk.models.target import Target, TargetCreate, TargetBrief # Added TargetBrief
from acunetix_sdk.models.scan import Scan, ScanCreate, SchedulingOptions
from acunetix_sdk.models.report import Report, ReportCreate, ReportSource
from acunetix_sdk.models.user import User, UserCreate
from acunetix_sdk.models.scan_profile import ScanProfile, ScanProfileCreateRequest, ScanProfileType # Changed ScanProfileCreate
from acunetix_sdk.models.report_template import ReportTemplate, ReportTemplateCreateRequest, ReportTemplateType # Changed ReportTemplateCreate
from acunetix_sdk.models.notification import Notification, NotificationData, NotificationType
from acunetix_sdk.models.common_settings import LoginSettings, CrawlSettings
from acunetix_sdk.models.pagination import PaginatedList, PaginationInfo

class TestTargetModels:
    def test_target_create_valid(self):
        data = {"address": "http://example.com", "description": "Test Target"}
        target = TargetCreate(**data)
        assert str(target.address) == "http://example.com" # Compare as string
        assert target.description == "Test Target"

    def test_target_create_invalid_url(self):
        with pytest.raises(ValidationError):
            TargetCreate(address="invalid-url", description="Test")

    def test_target_datetime_parsing(self):
        target_data = {
            "target_id": "uuid-target",
            "address": "http://example.com", 
            "description": "Test",
            "last_scan_date": "2023-01-01T12:00:00Z",
            "created_at": "2022-12-01T10:00:00.500Z"
        }
        target = Target(**target_data)
        assert isinstance(target.last_scan_date, datetime.datetime)
        assert target.last_scan_date.tzinfo is not None
        assert target.last_scan_date.tzinfo == datetime.timezone.utc
        assert isinstance(target.created_at, datetime.datetime)
        assert target.created_at.microsecond == 500000

# Add similar test classes for Scan, Report, User, ScanProfile, ReportTemplate, Notification, Pagination models.

class TestScanModels:
    def test_scan_create_with_schedule(self):
        schedule_data = {"start_date": "2024-01-01T10:00:00Z", "disable": False}
        scan_create_data = {
            "target_id": "00000000-0000-0000-0000-000000000000",  # Placeholder UUID
            "profile_id": "11111111-1111-1111-1111-111111111111", # Placeholder UUID
            "schedule": schedule_data
        }
        scan = ScanCreate(**scan_create_data)
        assert isinstance(scan.schedule, SchedulingOptions)
        assert isinstance(scan.schedule.start_date, datetime.datetime)

# ... more model tests ...

class TestPaginationModel:
    def test_paginated_list_targets(self):
        target_items = [
            TargetBrief(target_id="t1", address="http://ex1.com", description="d1"),
            TargetBrief(target_id="t2", address="http://ex2.com", description="d2")
        ]
        pagination_info = PaginationInfo(next_cursor="nextpage", count=2, total=10)
        paginated_result = PaginatedList[TargetBrief](items=target_items, pagination=pagination_info)
        
        assert len(paginated_result.items) == 2
        assert paginated_result.items[0].target_id == "t1"
        assert paginated_result.pagination.next_cursor == "nextpage"
