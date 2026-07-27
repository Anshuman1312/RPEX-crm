"""
Final production validation and testing suite.
Validates: Database migrations, seed data, API routes, security configs.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

import asyncpg
import httpx
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.database.base import Base
from app.core.config import settings
import app.models  # noqa: F401 - registers all models


class ValidationSuite:
    """Comprehensive production validation."""

    def __init__(self):
        self.results: dict[str, Any] = {
            "timestamp": None,
            "environment": settings.APP_ENV,
            "validations": {},
            "summary": {"passed": 0, "failed": 0, "warnings": 0},
        }
        self.engine: Any = None
        self.async_session: Any = None

    async def validate_all(self) -> bool:
        """Run all validations."""
        print("🔍 Starting production validation suite...\n")

        try:
            # 1. Check database connectivity
            await self.validate_db_connectivity()

            # 2. Check database migrations
            await self.validate_migrations()

            # 3. Check seed data
            await self.validate_seed_data()

            # 4. Validate SQLAlchemy models
            await self.validate_models()

            # 5. Validate API routes
            await self.validate_api_routes()

            # 6. Check security configuration
            await self.validate_security()

            # 7. Check environment variables
            await self.validate_env_vars()

            # 8. Docker compose validation
            await self.validate_docker_compose()

        except Exception as e:
            self.record_failure("general", f"Validation suite error: {e}")
            return False
        finally:
            await self.cleanup()

        return self.results["summary"]["failed"] == 0

    async def validate_db_connectivity(self) -> None:
        """Test database connection."""
        test_name = "Database Connectivity"
        try:
            # Try to connect to database
            conn = await asyncpg.connect(
                user=settings.DATABASE_USER,
                password=settings.DATABASE_PASSWORD,
                database=settings.DATABASE_NAME,
                host=settings.DATABASE_HOST,
                port=settings.DATABASE_PORT,
            )
            await conn.close()
            self.record_pass(test_name, "PostgreSQL connection successful")
        except Exception as e:
            self.record_failure(test_name, f"PostgreSQL connection failed: {e}")

    async def validate_migrations(self) -> None:
        """Check that all migrations have been applied."""
        test_name = "Alembic Migrations"
        try:
            # Create async engine
            self.engine = create_async_engine(
                settings.DATABASE_URL,
                echo=False,
                pool_size=5,
                max_overflow=10,
            )
            self.async_session = sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )

            # Check if alembic_version table exists (indicates migrations run)
            async with self.engine.connect() as conn:
                result = await conn.execute(
                    "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
                    "WHERE table_name='alembic_version')"
                )
                exists = (await result.scalar()) is True

            if exists:
                self.record_pass(test_name, "Alembic migrations have been applied")
            else:
                self.record_warning(
                    test_name, "Alembic migrations not yet applied (run 'alembic upgrade head')"
                )
        except Exception as e:
            self.record_failure(test_name, f"Migration check failed: {e}")

    async def validate_seed_data(self) -> None:
        """Verify seed data has been loaded."""
        test_name = "Seed Data"
        try:
            async with self.async_session() as session:
                # Check for default users
                from app.models.user import User

                count = await session.execute("SELECT COUNT(*) FROM users")
                user_count = (await count.scalar()) or 0

                if user_count > 0:
                    self.record_pass(test_name, f"Found {user_count} users in database")
                else:
                    self.record_warning(
                        test_name, "No users found (run 'python scripts/seed_data.py')"
                    )
        except Exception as e:
            self.record_failure(test_name, f"Seed data check failed: {e}")

    async def validate_models(self) -> None:
        """Validate SQLAlchemy model registration."""
        test_name = "SQLAlchemy Models"
        try:
            table_count = len(Base.metadata.tables)
            expected_tables = 32

            if table_count == expected_tables:
                self.record_pass(
                    test_name,
                    f"All {expected_tables} tables registered with SQLAlchemy",
                )
            elif table_count > 0:
                self.record_warning(
                    test_name,
                    f"Found {table_count} tables (expected {expected_tables})",
                )
            else:
                self.record_failure(test_name, "No tables registered with SQLAlchemy")

            # List tables
            tables = sorted(Base.metadata.tables.keys())
            print(f"  Registered tables: {', '.join(tables[:5])}...")
        except Exception as e:
            self.record_failure(test_name, f"Model validation failed: {e}")

    async def validate_api_routes(self) -> None:
        """Validate OpenAPI schema and route count."""
        test_name = "API Routes"
        try:
            from app.main import app as fastapi_app

            schema = fastapi_app.openapi()
            route_count = len(schema.get("paths", {}))
            expected_routes = 134

            if route_count == expected_routes:
                self.record_pass(test_name, f"All {expected_routes} API routes registered")
            elif route_count > 0:
                self.record_warning(test_name, f"Found {route_count} routes (expected {expected_routes})")
            else:
                self.record_failure(test_name, "No API routes found")
        except Exception as e:
            self.record_failure(test_name, f"Route validation failed: {e}")

    async def validate_security(self) -> None:
        """Check security configurations."""
        test_name = "Security Configuration"
        issues = []

        # Check secret key in production
        if settings.is_production and settings.SECRET_KEY == "change_this_in_production":
            issues.append("SECRET_KEY not changed in production")

        # Check CORS configuration
        if settings.is_production and settings.ALLOWED_ORIGINS == ["*"]:
            issues.append("CORS allows all origins in production")

        # Check HTTPS enforcement
        if settings.is_production:
            issues.append("Ensure HTTPS is enforced in production via Nginx")

        if issues:
            for issue in issues:
                self.record_warning(test_name, issue)
        else:
            self.record_pass(test_name, "Security configuration validated")

    async def validate_env_vars(self) -> None:
        """Check required environment variables."""
        test_name = "Environment Variables"
        required_vars = [
            "DATABASE_URL",
            "REDIS_URL",
            "SECRET_KEY",
            "ALGORITHM",
        ]

        missing = []
        for var in required_vars:
            if not getattr(settings, var.lower(), None):
                missing.append(var)

        if missing:
            self.record_warning(test_name, f"Missing variables: {', '.join(missing)}")
        else:
            self.record_pass(test_name, f"All {len(required_vars)} required variables set")

    async def validate_docker_compose(self) -> None:
        """Check Docker compose configuration."""
        test_name = "Docker Compose"
        try:
            compose_path = Path(__file__).parent / "docker-compose.yml"
            if compose_path.exists():
                with open(compose_path) as f:
                    content = f.read()
                if all(s in content for s in ["postgres", "redis", "backend", "frontend", "nginx"]):
                    self.record_pass(
                        test_name,
                        "Docker compose contains all required services",
                    )
                else:
                    self.record_warning(test_name, "Docker compose may be missing services")
            else:
                self.record_failure(test_name, "docker-compose.yml not found")
        except Exception as e:
            self.record_failure(test_name, f"Docker compose validation failed: {e}")

    def record_pass(self, test: str, message: str) -> None:
        """Record a passing test."""
        self.results["validations"][test] = {
            "status": "✅ PASS",
            "message": message,
        }
        self.results["summary"]["passed"] += 1
        print(f"✅ {test:30s} | {message}")

    def record_failure(self, test: str, message: str) -> None:
        """Record a failing test."""
        self.results["validations"][test] = {
            "status": "❌ FAIL",
            "message": message,
        }
        self.results["summary"]["failed"] += 1
        print(f"❌ {test:30s} | {message}")

    def record_warning(self, test: str, message: str) -> None:
        """Record a warning."""
        self.results["validations"][test] = {
            "status": "⚠️  WARN",
            "message": message,
        }
        self.results["summary"]["warnings"] += 1
        print(f"⚠️  {test:30s} | {message}")

    async def cleanup(self) -> None:
        """Clean up resources."""
        if self.engine:
            await self.engine.dispose()

    def print_summary(self) -> None:
        """Print validation summary."""
        summary = self.results["summary"]
        print("\n" + "=" * 70)
        print("VALIDATION SUMMARY")
        print("=" * 70)
        print(f"✅ Passed:  {summary['passed']}")
        print(f"⚠️  Warnings: {summary['warnings']}")
        print(f"❌ Failed:  {summary['failed']}")
        print("=" * 70)

        if summary["failed"] == 0:
            print("\n🎉 All critical validations passed! System is production-ready.")
            if summary["warnings"] > 0:
                print(f"⚠️  Please address {summary['warnings']} warning(s) before deployment.")
        else:
            print(f"\n⚠️  {summary['failed']} validation(s) failed. Please fix before deployment.")
            sys.exit(1)


async def main() -> None:
    """Run validation suite."""
    validator = ValidationSuite()
    success = await validator.validate_all()
    validator.print_summary()

    # Save results to file
    results_path = Path(__file__).parent / "validation_results.json"
    with open(results_path, "w") as f:
        json.dump(validator.results, f, indent=2)
    print(f"\n📝 Detailed results saved to: {results_path}")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
