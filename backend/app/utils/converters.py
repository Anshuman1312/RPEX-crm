from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional, TypeVar, Generic

import uuid

T = TypeVar("T")


class TypeConverter:
    """Helper class for type conversions."""

    @staticmethod
    def to_uuid(value: str | uuid.UUID | None) -> uuid.UUID | None:
        """Convert string to UUID."""
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(value)

    @staticmethod
    def to_str(value: Any) -> str:
        """Convert any value to string."""
        if value is None:
            return ""
        return str(value)

    @staticmethod
    def to_int(value: Any, default: int = 0) -> int:
        """Convert to int with fallback."""
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def to_float(value: Any, default: float = 0.0) -> float:
        """Convert to float with fallback."""
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def to_decimal(value: Any, default: Decimal = Decimal("0")) -> Decimal:
        """Convert to Decimal with fallback."""
        try:
            return Decimal(str(value))
        except Exception:
            return default

    @staticmethod
    def to_bool(value: Any) -> bool:
        """Convert to bool."""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "yes", "1", "on")
        return bool(value)


class DateTimeConverter:
    """Helper class for datetime conversions."""

    @staticmethod
    def now_utc() -> datetime:
        """Get current UTC time."""
        return datetime.now(timezone.utc)

    @staticmethod
    def to_iso_string(dt: datetime | None) -> str | None:
        """Convert datetime to ISO 8601 string."""
        if dt is None:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()

    @staticmethod
    def from_iso_string(s: str) -> datetime:
        """Parse ISO 8601 string to datetime."""
        # Handle formats with and without microseconds
        if "." in s:
            if s.endswith("Z"):
                return datetime.fromisoformat(s.replace("Z", "+00:00"))
            return datetime.fromisoformat(s)
        else:
            if s.endswith("Z"):
                return datetime.fromisoformat(s.replace("Z", "+00:00"))
            return datetime.fromisoformat(s)

    @staticmethod
    def to_timestamp(dt: datetime | None) -> int | None:
        """Convert datetime to Unix timestamp (seconds)."""
        if dt is None:
            return None
        return int(dt.timestamp())

    @staticmethod
    def from_timestamp(ts: int | float) -> datetime:
        """Convert Unix timestamp to datetime."""
        return datetime.fromtimestamp(ts, tz=timezone.utc)


class CurrencyConverter:
    """Helper class for currency/money conversions."""

    @staticmethod
    def format_currency(amount: Decimal | float, currency: str = "INR", decimal_places: int = 2) -> str:
        """Format amount as currency string."""
        if isinstance(amount, float):
            amount = Decimal(str(amount))

        # Format with decimal places
        formatted = f"{amount:.{decimal_places}f}"

        # Add currency symbol
        symbols = {
            "INR": "₹",
            "USD": "$",
            "EUR": "€",
            "GBP": "£",
        }
        symbol = symbols.get(currency, currency)

        return f"{symbol} {formatted}"

    @staticmethod
    def parse_currency(value: str) -> Decimal:
        """Parse currency string to Decimal."""
        # Remove currency symbols and whitespace
        cleaned = "".join(c for c in value if c.isdigit() or c in ".,")
        # Replace comma with dot if needed
        cleaned = cleaned.replace(",", ".")
        return Decimal(cleaned)

    @staticmethod
    def convert_currency(
        amount: Decimal | float, from_rate: float, to_rate: float
    ) -> Decimal:
        """Convert between currencies using exchange rates."""
        amount = Decimal(str(amount))
        conversion_rate = Decimal(str(to_rate / from_rate))
        return (amount * conversion_rate).quantize(Decimal("0.01"))


class EnumConverter:
    """Helper class for enum conversions."""

    @staticmethod
    def enum_to_value(enum_obj: Any) -> str:
        """Get enum value."""
        if hasattr(enum_obj, "value"):
            return enum_obj.value
        return str(enum_obj)

    @staticmethod
    def value_to_enum(value: str, enum_class: type):
        """Convert value to enum instance."""
        try:
            return enum_class(value)
        except ValueError:
            # Return None or raise depending on needs
            return None

    @staticmethod
    def enum_list_to_values(enum_list: list) -> list[str]:
        """Convert list of enums to their values."""
        return [EnumConverter.enum_to_value(e) for e in enum_list]

    @staticmethod
    def values_to_enum_list(values: list[str], enum_class: type) -> list:
        """Convert list of values to enum instances."""
        result = []
        for value in values:
            enum_obj = EnumConverter.value_to_enum(value, enum_class)
            if enum_obj:
                result.append(enum_obj)
        return result


class DictConverter:
    """Helper class for dict/object conversions."""

    @staticmethod
    def model_to_dict(obj: Any, exclude: Optional[set[str]] = None) -> dict:
        """Convert Pydantic model or ORM object to dict."""
        exclude = exclude or set()

        if hasattr(obj, "model_dump"):
            # Pydantic v2
            return obj.model_dump(exclude=exclude)
        elif hasattr(obj, "__dict__"):
            # ORM or regular object
            result = {}
            for key, value in obj.__dict__.items():
                if key.startswith("_") or key in exclude:
                    continue
                result[key] = value
            return result

        return {}

    @staticmethod
    def dict_to_model(data: dict, model_class: type[T]) -> T:
        """Convert dict to Pydantic model."""
        return model_class(**data)

    @staticmethod
    def merge_dicts(*dicts: dict) -> dict:
        """Merge multiple dicts (later dicts override earlier ones)."""
        result = {}
        for d in dicts:
            result.update(d)
        return result

    @staticmethod
    def pick_keys(data: dict, keys: list[str]) -> dict:
        """Extract only specified keys from dict."""
        return {k: data[k] for k in keys if k in data}

    @staticmethod
    def omit_keys(data: dict, keys: list[str]) -> dict:
        """Remove specified keys from dict."""
        return {k: v for k, v in data.items() if k not in keys}


class PhoneConverter:
    """Helper class for phone number conversions."""

    @staticmethod
    def normalize_phone(phone: str, country_code: str = "+91") -> str:
        """Normalize phone number to international format."""
        # Remove all non-digits
        digits = "".join(c for c in phone if c.isdigit())

        # Remove country code if present
        if digits.startswith("91"):
            digits = digits[2:]

        # Pad to 10 digits if shorter
        if len(digits) < 10:
            digits = digits.zfill(10)

        # Take last 10 digits
        digits = digits[-10:]

        return f"{country_code}{digits}"

    @staticmethod
    def format_phone(phone: str) -> str:
        """Format phone number for display."""
        phone = PhoneConverter.normalize_phone(phone)
        # +91-XXXXX-XXXXX
        return f"{phone[:3]}-{phone[3:8]}-{phone[8:]}"

    @staticmethod
    def validate_phone_length(phone: str) -> bool:
        """Check if phone has valid length."""
        digits = "".join(c for c in phone if c.isdigit())
        return 10 <= len(digits) <= 15
