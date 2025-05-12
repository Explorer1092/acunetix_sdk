from typing import Optional, Any
import datetime

def parse_datetime_string(value: Any) -> Optional[datetime.datetime]:
    """Parses common ISO 8601 datetime string formats into datetime objects."""
    if value is None:
        return None
    if isinstance(value, datetime.datetime):
        return value
    if not isinstance(value, str):
        return None # Or raise ValueError

    # Common Acunetix/API formats (may include Z for UTC or +/-HH:MM offset)
    # Example formats: 
    # "2023-04-12T10:30:00Z"
    # "2023-04-12T10:30:00.123Z"
    # "2023-04-12T10:30:00+02:00"
    # "2023-04-12 10:30:00" (less common in modern APIs but possible)
    
    # Try with Z and fractional seconds
    # Attempt to parse as full ISO 8601 datetime
    try:
        if value.endswith('Z'):
            # fromisoformat in Python 3.7+ handles 'Z' directly if it's at the end of a full datetime string
            # For older versions or more complex 'Z' scenarios, replacing 'Z' with '+00:00' is safer.
            # However, datetime.fromisoformat itself should handle 'Z' correctly for compliant strings.
            # Let's try direct fromisoformat first for simplicity and standard compliance.
            # If it fails, specific handling for 'Z' might be needed for older Python or non-standard 'Z'.
            # For now, assuming standard ISO 8601 where 'Z' means UTC.
            if '.' in value and value.rfind('.') < value.rfind('Z'): # Check if Z is after fractional seconds
                 return datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
            return datetime.datetime.fromisoformat(value) # Python 3.7+ handles 'Z'
    except ValueError:
        pass # Fall through to next try

    # Attempt to parse as ISO 8601 date (YYYY-MM-DD)
    try:
        return datetime.datetime.strptime(value, '%Y-%m-%d')
    except ValueError:
        pass # Fall through

    # Add more formats if needed
    # Example: "YYYY-MM-DD HH:MM:SS" (space instead of T)
    try:
        return datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        pass

    # If all parsing attempts fail
    # Depending on strictness, either return None or raise ValueError
    # For now, returning None to be lenient, as Pydantic will handle validation errors if field is required.
    return None
