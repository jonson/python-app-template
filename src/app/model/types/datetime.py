import sqlalchemy.types as types
import datetime


class UTCTimestamp(types.TypeDecorator):

    impl = types.TIMESTAMP(timezone=True)

    cache_ok = True

    def process_bind_param(self, value: datetime.datetime, dialect):
        # Convert incoming value to UTC
        assert value.tzinfo is not None, "Timestamp must be timezone-aware"
        return value.astimezone(datetime.timezone.utc)

    def process_result_value(self, value, dialect):
        # Ensure the result is in UTC
        assert value.tzinfo is not None
        return value.astimezone(datetime.timezone.utc)
