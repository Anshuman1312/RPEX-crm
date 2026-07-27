from __future__ import annotations

from typing import Any, Optional, Callable
from datetime import datetime

from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.orm import InspectionAttr
from sqlalchemy.sql.expression import BinaryExpression


class QueryBuilder:
    """
    Fluent query builder for constructing complex SQLAlchemy queries.

    Supports filtering, sorting, pagination, and full-text search.
    """

    def __init__(self, model: type):
        self.model = model
        self.query = select(model)
        self.filters: list[BinaryExpression] = []
        self.order_bys: list = []
        self._skip = 0
        self._limit = None

    def filter(self, *conditions: BinaryExpression) -> QueryBuilder:
        """Add WHERE conditions."""
        self.filters.extend(conditions)
        return self

    def filter_equal(self, field_name: str, value: Any) -> QueryBuilder:
        """Add equality filter."""
        if value is not None:
            field = getattr(self.model, field_name)
            self.filters.append(field == value)
        return self

    def filter_in(self, field_name: str, values: list) -> QueryBuilder:
        """Add IN filter."""
        if values:
            field = getattr(self.model, field_name)
            self.filters.append(field.in_(values))
        return self

    def filter_like(self, field_name: str, value: str) -> QueryBuilder:
        """Add LIKE filter (case-insensitive)."""
        if value:
            field = getattr(self.model, field_name)
            self.filters.append(field.ilike(f"%{value}%"))
        return self

    def filter_date_range(
        self, field_name: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> QueryBuilder:
        """Add date range filter."""
        field = getattr(self.model, field_name)

        if start_date:
            self.filters.append(field >= start_date)

        if end_date:
            self.filters.append(field <= end_date)

        return self

    def filter_number_range(
        self, field_name: str, min_value: Optional[float] = None, max_value: Optional[float] = None
    ) -> QueryBuilder:
        """Add numeric range filter."""
        field = getattr(self.model, field_name)

        if min_value is not None:
            self.filters.append(field >= min_value)

        if max_value is not None:
            self.filters.append(field <= max_value)

        return self

    def filter_or(self, *conditions: BinaryExpression) -> QueryBuilder:
        """Add OR condition (groups multiple conditions)."""
        if conditions:
            self.filters.append(or_(*conditions))
        return self

    def sort_by(self, field_name: str, direction: str = "asc") -> QueryBuilder:
        """Add ORDER BY clause."""
        field = getattr(self.model, field_name)

        if direction.lower() == "desc":
            self.order_bys.append(desc(field))
        else:
            self.order_bys.append(asc(field))

        return self

    def paginate(self, skip: int, limit: int) -> QueryBuilder:
        """Add pagination."""
        self._skip = skip
        self._limit = limit
        return self

    def skip(self, count: int) -> QueryBuilder:
        """Set OFFSET."""
        self._skip = count
        return self

    def limit(self, count: int) -> QueryBuilder:
        """Set LIMIT."""
        self._limit = count
        return self

    def build(self):
        """Build the final query."""
        query = self.query

        # Apply filters
        if self.filters:
            query = query.where(and_(*self.filters))

        # Apply sort
        if self.order_bys:
            query = query.order_by(*self.order_bys)

        # Apply pagination
        if self._skip:
            query = query.offset(self._skip)

        if self._limit:
            query = query.limit(self._limit)

        return query

    def build_count(self):
        """Build a count query (ignores pagination)."""
        query = select(func.count()).select_from(self.model)

        if self.filters:
            query = query.where(and_(*self.filters))

        return query


class FullTextSearchBuilder:
    """
    Helper for full-text search across multiple fields.

    Note: For PostgreSQL, consider using pg_search extension or native FTS.
    This is a basic multi-field LIKE implementation suitable for SQLite/MySQL.
    """

    def __init__(self, model: type, search_query: str):
        self.model = model
        self.search_query = search_query.strip()
        self.conditions = []

    def search_in(self, *field_names: str) -> FullTextSearchBuilder:
        """Add fields to search in."""
        for field_name in field_names:
            field = getattr(self.model, field_name, None)
            if field is not None:
                self.conditions.append(field.ilike(f"%{self.search_query}%"))

        return self

    def build(self) -> BinaryExpression | None:
        """Build OR condition for all search fields."""
        if not self.conditions:
            return None

        return or_(*self.conditions)


class AggregationBuilder:
    """
    Helper for building aggregation queries.

    Example: Count leads by status, sum payments by month.
    """

    def __init__(self, model: type):
        self.model = model
        self.query = select(model)
        self.group_bys = []
        self.aggregates = {}

    def group_by(self, *field_names: str) -> AggregationBuilder:
        """Set GROUP BY fields."""
        for field_name in field_names:
            field = getattr(self.model, field_name)
            self.group_bys.append(field)

        return self

    def count(self, alias: str = "count") -> AggregationBuilder:
        """Add COUNT(*)."""
        self.aggregates[alias] = func.count()
        return self

    def sum(self, field_name: str, alias: str | None = None) -> AggregationBuilder:
        """Add SUM(field)."""
        field = getattr(self.model, field_name)
        alias = alias or f"sum_{field_name}"
        self.aggregates[alias] = func.sum(field)
        return self

    def avg(self, field_name: str, alias: str | None = None) -> AggregationBuilder:
        """Add AVG(field)."""
        field = getattr(self.model, field_name)
        alias = alias or f"avg_{field_name}"
        self.aggregates[alias] = func.avg(field)
        return self

    def min(self, field_name: str, alias: str | None = None) -> AggregationBuilder:
        """Add MIN(field)."""
        field = getattr(self.model, field_name)
        alias = alias or f"min_{field_name}"
        self.aggregates[alias] = func.min(field)
        return self

    def max(self, field_name: str, alias: str | None = None) -> AggregationBuilder:
        """Add MAX(field)."""
        field = getattr(self.model, field_name)
        alias = alias or f"max_{field_name}"
        self.aggregates[alias] = func.max(field)
        return self

    def build(self):
        """Build aggregation query."""
        select_clauses = list(self.group_bys) + list(self.aggregates.values())
        query = select(*select_clauses)

        if self.group_bys:
            query = query.group_by(*self.group_bys)

        return query
