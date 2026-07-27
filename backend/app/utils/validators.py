from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from app.core.exceptions import ValidationException


class DateValidator:
    """Validators for date/time fields."""

    @staticmethod
    def validate_future_date(date: datetime, field_name: str = "date") -> None:
        """Ensure date is in the future."""
        now = datetime.now(timezone.utc)
        if date <= now:
            raise ValidationException(f"{field_name} must be in the future.", field=field_name)

    @staticmethod
    def validate_past_date(date: datetime, field_name: str = "date") -> None:
        """Ensure date is in the past."""
        now = datetime.now(timezone.utc)
        if date > now:
            raise ValidationException(f"{field_name} must be in the past.", field=field_name)

    @staticmethod
    def validate_date_range(
        start_date: datetime, end_date: datetime, start_name: str = "start_date", end_name: str = "end_date"
    ) -> None:
        """Ensure start_date < end_date."""
        if start_date >= end_date:
            raise ValidationException(f"{start_name} must be before {end_name}.", field=start_name)

    @staticmethod
    def validate_business_hours(
        date: datetime, start_hour: int = 9, end_hour: int = 18, field_name: str = "date"
    ) -> None:
        """Ensure date/time falls within business hours."""
        if not (start_hour <= date.hour < end_hour):
            raise ValidationException(
                f"{field_name} must be within business hours ({start_hour}:00 - {end_hour}:00).",
                field=field_name,
            )


class AmountValidator:
    """Validators for monetary amounts."""

    @staticmethod
    def validate_positive(amount: Decimal | float, field_name: str = "amount") -> None:
        """Ensure amount is positive."""
        if amount <= 0:
            raise ValidationException(f"{field_name} must be greater than 0.", field=field_name)

    @staticmethod
    def validate_non_negative(amount: Decimal | float, field_name: str = "amount") -> None:
        """Ensure amount is non-negative."""
        if amount < 0:
            raise ValidationException(f"{field_name} must not be negative.", field=field_name)

    @staticmethod
    def validate_amount_range(
        amount: Decimal | float,
        min_amount: Optional[Decimal | float] = None,
        max_amount: Optional[Decimal | float] = None,
        field_name: str = "amount",
    ) -> None:
        """Validate amount is within range."""
        if min_amount is not None and amount < min_amount:
            raise ValidationException(f"{field_name} must be at least {min_amount}.", field=field_name)

        if max_amount is not None and amount > max_amount:
            raise ValidationException(f"{field_name} must not exceed {max_amount}.", field=field_name)

    @staticmethod
    def validate_decimal_places(amount: Decimal, max_places: int = 2, field_name: str = "amount") -> None:
        """Ensure amount has max decimal places."""
        if isinstance(amount, Decimal):
            _, digits, exponent = amount.as_tuple()
            decimal_places = -exponent if exponent < 0 else 0

            if decimal_places > max_places:
                raise ValidationException(
                    f"{field_name} must have at most {max_places} decimal places.",
                    field=field_name,
                )


class ContactValidator:
    """Validators for contact information."""

    @staticmethod
    def validate_phone(phone: str, field_name: str = "phone") -> None:
        """Validate phone number format."""
        # Basic validation: 10+ digits
        digits = "".join(c for c in phone if c.isdigit())

        if len(digits) < 10:
            raise ValidationException(f"{field_name} must have at least 10 digits.", field=field_name)

    @staticmethod
    def validate_pincode(pincode: str, field_name: str = "pincode") -> None:
        """Validate postal code format (India 6-digit)."""
        if not pincode.isdigit() or len(pincode) != 6:
            raise ValidationException(f"{field_name} must be a 6-digit number.", field=field_name)


class TextValidator:
    """Validators for text fields."""

    @staticmethod
    def validate_length(
        text: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        field_name: str = "text",
    ) -> None:
        """Validate string length."""
        if min_length is not None and len(text) < min_length:
            raise ValidationException(f"{field_name} must be at least {min_length} characters.", field=field_name)

        if max_length is not None and len(text) > max_length:
            raise ValidationException(f"{field_name} must not exceed {max_length} characters.", field=field_name)

    @staticmethod
    def validate_non_empty(text: str, field_name: str = "text") -> None:
        """Ensure text is not empty or whitespace."""
        if not text or not text.strip():
            raise ValidationException(f"{field_name} cannot be empty.", field=field_name)

    @staticmethod
    def validate_alphanumeric(text: str, field_name: str = "text", allow_special: str = "") -> None:
        """Validate text contains only alphanumeric + optional special chars."""
        allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ") | set(allow_special)

        if not all(c in allowed for c in text):
            raise ValidationException(
                f"{field_name} contains invalid characters. Allowed: alphanumeric{' and ' + allow_special if allow_special else ''}",
                field=field_name,
            )


class StateValidator:
    """Validators for state machine transitions."""

    @staticmethod
    def validate_state_transition(
        current_state: str,
        target_state: str,
        allowed_transitions: dict[str, list[str]],
        entity_name: str = "Entity",
    ) -> None:
        """
        Validate state transition is allowed.

        Args:
            current_state: Current state
            target_state: Desired target state
            allowed_transitions: dict mapping from_state -> [allowed_to_states]
            entity_name: Name for error message
        """
        if current_state not in allowed_transitions:
            raise ValidationException(
                f"{entity_name} cannot transition from state '{current_state}'.",
                field="state",
            )

        allowed = allowed_transitions[current_state]
        if target_state not in allowed:
            raise ValidationException(
                f"{entity_name} cannot transition from '{current_state}' to '{target_state}'. "
                f"Allowed: {', '.join(allowed)}",
                field="state",
            )


class RangeValidator:
    """Validators for numeric ranges."""

    @staticmethod
    def validate_percentage(value: float | int, field_name: str = "percentage") -> None:
        """Validate value is between 0 and 100."""
        if not (0 <= value <= 100):
            raise ValidationException(f"{field_name} must be between 0 and 100.", field=field_name)

    @staticmethod
    def validate_in_range(
        value: int | float,
        min_val: int | float,
        max_val: int | float,
        field_name: str = "value",
    ) -> None:
        """Validate value is within range."""
        if not (min_val <= value <= max_val):
            raise ValidationException(
                f"{field_name} must be between {min_val} and {max_val}.",
                field=field_name,
            )
