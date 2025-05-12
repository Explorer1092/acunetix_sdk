from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr, Field, field_validator, conlist # Added conlist
import datetime
from .utils import parse_datetime_string

class RoleMapping(BaseModel):
    """
    Represents a role mapping for a user.
    Corresponds to #/definitions/RoleMapping in API spec.
    NOTE: API documentation does not specify how the server handles a client-provided 'role_mapping_id'
    during creation or update operations. It might be ignored, used if unique, or cause an error.
    Typically, for new mappings, the ID is server-generated.
    """
    role_mapping_id: Optional[str] = Field(None, description="Role Mapping ID (usually read-only)")
    role_id: str = Field(..., description="Role assigned to a User")
    access_all_targets: Optional[bool] = Field(False, description="User has access to all Targets")
    target_group_ids: Optional[List[str]] = Field(default_factory=list, description="Target Groups available to a User (list of UUIDs)")

class RoleMappingCreate(BaseModel):
    """
    Data for creating a role mapping.
    May omit read-only fields like role_mapping_id.
    """
    role_id: str = Field(..., description="Role assigned to a User")
    access_all_targets: Optional[bool] = Field(False, description="User has access to all Targets")
    target_group_ids: Optional[List[str]] = Field(default_factory=list, description="Target Groups available to a User (list of UUIDs)")


class UserBrief(BaseModel):
    user_id: str
    first_name: str
    last_name: str
    email: EmailStr
    enabled: bool # Changed from is_active, alias removed as field name matches API 'enabled'
    # created_at and updated_at removed as they are not in API's ChildUser model

class User(UserBrief):
    # More detailed fields for a user, aligned with API's ChildUser
    # last_login removed as it's not in API's ChildUser model
    role_mappings: Optional[List[RoleMapping]] = Field(default_factory=list) # Changed from roles: List[str]
    user_groups: Optional[List[str]] = Field(default_factory=list, description="List of user group UUIDs user belongs to")
    
    totp_enabled: Optional[bool] = Field(None, description="Is TOTP enabled for the user (read-only)")
    locked: Optional[int] = Field(None, description="Lock status of the user account (read-only)") # API type was integer
    invite_id: Optional[str] = Field(None, description="Invite ID if user was invited")
    invite_expired: Optional[bool] = Field(None, description="If the invite has expired")
    expiration_date: Optional[datetime.datetime] = Field(None, description="Account expiration date")
    sso_exemption: Optional[bool] = Field(None, description="SSO exemption status")


    @field_validator("expiration_date", mode="before")
    @classmethod
    def _validate_optional_datetimes(cls, value: Any) -> Optional[datetime.datetime]:
        return parse_datetime_string(value)

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str # Password is required on creation
    role_mappings: Optional[List[RoleMappingCreate]] = Field(default_factory=list) # Using RoleMappingCreate
    enabled: Optional[bool] = True # Changed from is_active
    # send_email parameter will be handled in the resource method, not the model

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role_mappings: Optional[List[RoleMappingCreate]] = None # Using RoleMappingCreate for updates too
    enabled: Optional[bool] = None # Changed from is_active
    # Password update is often a separate endpoint/method for security reasons

class ChildUserIdList(BaseModel):
    """
    Corresponds to #/definitions/ChildUserIdList in API spec.
    Used for bulk operations on users.
    """
    user_id_list: List[str] = Field(..., description="List of user UUIDs")

# --- User Group Models ---
class UserGroupStats(BaseModel):
    """Corresponds to #/definitions/UserGroupStats"""
    user_count: Optional[int] = None

class UserGroup(BaseModel): # Used for POST and PATCH /user_groups
    """
    Corresponds to #/definitions/UserGroup in API spec.
    Used for creating/updating a user group.
    """
    name: str = Field(..., max_length=128)
    description: str = Field(..., max_length=256) # API spec marks description as required
    role_mappings: Optional[List[RoleMapping]] = Field(default_factory=list) # API spec uses RoleMapping
    user_ids: Optional[List[Optional[str]]] = Field(default_factory=list, description="List of user UUIDs, may contain None")

class UserGroupUpdate(BaseModel):
    """Model for updating a user group, all fields are optional."""
    name: Optional[str] = Field(None, max_length=128)
    description: Optional[str] = Field(None, max_length=256)
    role_mappings: Optional[List[RoleMapping]] = None # Allow explicit None to clear, or list to update
    user_ids: Optional[List[Optional[str]]] = None # Allow explicit None to clear, or list to update

class UserGroupDetails(BaseModel): # Used for GET /user_groups/{id} and in UserGroupsList
    """Corresponds to #/definitions/UserGroupDetails in API spec."""
    user_group_id: str = Field(..., description="User Group UUID")
    name: str = Field(..., max_length=128)
    description: Optional[str] = Field(None, max_length=256)
    created_at: Optional[datetime.datetime] = Field(None, alias="created") # API uses 'created'
    owner_id: Optional[str] = Field(None, description="Owner UUID")
    creator_id: Optional[str] = Field(None, description="Creator UUID")
    user_ids: Optional[List[Optional[str]]] = Field(default_factory=list) # Allow None in list
    role_mappings: Optional[List[RoleMapping]] = Field(default_factory=list) # API returns full RoleMapping
    stats: Optional[UserGroupStats] = None

    @field_validator("created_at", mode="before")
    @classmethod
    def _validate_created_at(cls, value: Any) -> Optional[datetime.datetime]:
        return parse_datetime_string(value)

# UserGroupsList is handled by PaginatedList[UserGroupDetails] in resource methods.

class UserToUserGroupDetails(BaseModel):
    """Corresponds to #/definitions/UserToUserGroupDetails"""
    user_ids: Optional[List[Optional[str]]] = Field(default_factory=list) # Allow None in list
    user_group_id: Optional[str] = None # UUID

class RoleMappingList(BaseModel): # Request body for adding roles to user group
    """Corresponds to #/definitions/RoleMappingList"""
    role_mappings: List[RoleMapping] # API spec uses RoleMapping

class RoleMappingIdList(BaseModel): # Request body for removing roles from user group
    """Corresponds to #/definitions/RoleMappingIdList"""
    role_mapping_ids: List[str] = Field(..., description="List of RoleMapping UUIDs to remove")

class UserGroupRoleMappings(BaseModel): # Response for adding roles to user group
    """Corresponds to #/definitions/UserGroupRoleMappings"""
    user_group_id: Optional[str] = None # UUID
    role_mappings: Optional[List[RoleMapping]] = Field(default_factory=list)

# --- Role Models ---
class RoleStats(BaseModel): # Already defined for UserGroupStats, ensure it's suitable or make specific
    """Corresponds to #/definitions/RoleStats"""
    user_count: Optional[int] = None
    group_count: Optional[int] = None
    all_user_count: Optional[int] = None # API spec shows this for RoleDetails

class Role(BaseModel): # Used for POST and PATCH /roles
    """
    Corresponds to #/definitions/Role in API spec.
    Used for creating/updating a role.
    """
    name: str = Field(..., max_length=128)
    description: str = Field(..., max_length=256) # API spec marks description as required for Role
    permissions: conlist(str, max_length=100) = Field(..., description="List of permission names/IDs")

class RoleUpdate(BaseModel):
    """Model for updating a role, all fields are optional."""
    name: Optional[str] = Field(None, max_length=128)
    description: Optional[str] = Field(None, max_length=256)
    permissions: Optional[conlist(str, max_length=100)] = None

class RoleDetails(BaseModel): # Used for GET /roles/{id} and in RolesList
    """Corresponds to #/definitions/RoleDetails in API spec."""
    role_id: str = Field(..., description="Role UUID")
    name: str = Field(..., max_length=128)
    description: Optional[str] = Field(None, max_length=256) # Description is optional in RoleDetails
    created_at: Optional[datetime.datetime] = None
    owner_id: Optional[str] = Field(None, description="Owner UUID")
    creator_id: Optional[str] = Field(None, description="Creator UUID")
    permissions: Optional[conlist(str, max_length=100)] = Field(default_factory=list)
    stats: Optional[RoleStats] = None

    @field_validator("created_at", mode="before")
    @classmethod
    def _validate_role_created_at(cls, value: Any) -> Optional[datetime.datetime]:
        return parse_datetime_string(value)

# RolesList is handled by PaginatedList[RoleDetails] in resource methods.

class PermissionDetailEntry(BaseModel):
    """Corresponds to #/definitions/PermissionDetailEntry"""
    category: Optional[str] = Field(None, max_length=128)
    name: Optional[str] = Field(None, max_length=128)
    description: Optional[str] = Field(None, max_length=256)

class PermissionsList(BaseModel):
    """Corresponds to #/definitions/PermissionsList"""
    permissions: Optional[List[PermissionDetailEntry]] = Field(default_factory=list)

# --- Backwards-compatibility alias ---
UserResponse = User
