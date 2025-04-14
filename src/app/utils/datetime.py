from datetime import datetime, timezone


def to_utc_datetime(value: datetime) -> datetime:
    """Converts a datetime value into a one in the UTC zone.
    If the value does not have a timezone set, it is assumed the timezone is UTC."""

    # Value already has UTC timezone info. Return as-is.
    if value.tzinfo == timezone.utc:
        return value

    # If no timezone info, assume it's UTC and add UTC timezone info.
    if not value.tzinfo:
        return value.replace(tzinfo=timezone.utc)

    # Convert non-UTC datetime value to UTC.
    return value.astimezone(timezone.utc)


def datetime_utcnow() -> datetime:
    """Returns the present UTC datetime value with explicit UTC timezone info."""
    return datetime.now(timezone.utc)
