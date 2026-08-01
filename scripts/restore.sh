#!/bin/bash
# Database Restore Script for RPEX CRM PostgreSQL
# Usage: ./restore.sh [backup_file]
# Restores PostgreSQL database from a gzipped SQL backup file

set -e

BACKUP_FILE="${1:?Backup file path required. Usage: ./restore.sh <backup_file.sql.gz>}"
DB_USER=${DB_USER:-rpex}
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-rpex_crm}
RESTORE_LOG="./restore_$(date +%s).log"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Validation
if [ ! -f "$BACKUP_FILE" ]; then
  echo -e "${RED}✗ Backup file not found: $BACKUP_FILE${NC}"
  exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔄 RPEX CRM Database Restore"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Backup File: $BACKUP_FILE"
echo "Database: $DB_NAME @ $DB_HOST:$DB_PORT"
echo "User: $DB_USER"
echo ""

# Show backup file info
BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
BACKUP_DATE=$(stat -f %Sm -t "%Y-%m-%d %H:%M:%S" "$BACKUP_FILE" 2>/dev/null || stat -c %y "$BACKUP_FILE" 2>/dev/null || echo "unknown")
echo -e "${BLUE}ℹ File size: $BACKUP_SIZE${NC}"
echo -e "${BLUE}ℹ Backup date: $BACKUP_DATE${NC}"
echo ""

# Confirmation
echo -e "${YELLOW}⚠ WARNING: This will overwrite all data in database '$DB_NAME'!${NC}"
read -p "Continue? [yes/no]: " -r
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
  echo "Restore cancelled."
  exit 0
fi

echo ""
echo "⏳ Dropping existing database connections..."
PGPASSWORD=$DB_PASSWORD psql \
  --host="$DB_HOST" \
  --port="$DB_PORT" \
  --username="$DB_USER" \
  --dbname=postgres \
  --command="
    SELECT pg_terminate_backend(pg_stat_activity.pid)
    FROM pg_stat_activity
    WHERE pg_stat_activity.datname = '$DB_NAME'
    AND pid <> pg_backend_pid();
  " 2>&1 | grep -v "^$" || true

echo "⏳ Dropping database..."
PGPASSWORD=$DB_PASSWORD psql \
  --host="$DB_HOST" \
  --port="$DB_PORT" \
  --username="$DB_USER" \
  --dbname=postgres \
  --command="DROP DATABASE IF EXISTS $DB_NAME;" 2>/dev/null || true

echo "⏳ Creating database..."
PGPASSWORD=$DB_PASSWORD psql \
  --host="$DB_HOST" \
  --port="$DB_PORT" \
  --username="$DB_USER" \
  --dbname=postgres \
  --command="CREATE DATABASE $DB_NAME OWNER $DB_USER;"

echo "⏳ Restoring from backup..."
if gunzip -c "$BACKUP_FILE" | PGPASSWORD=$DB_PASSWORD psql \
  --host="$DB_HOST" \
  --port="$DB_PORT" \
  --username="$DB_USER" \
  --dbname="$DB_NAME" \
  2>"$RESTORE_LOG" > /dev/null; then
  echo -e "${GREEN}✓ Restore successful!${NC}"
else
  echo -e "${RED}✗ Restore failed!${NC}"
  echo "See logs: $RESTORE_LOG"
  cat "$RESTORE_LOG"
  exit 1
fi

echo ""
echo "⏳ Running post-restore checks..."

# Verify table count
TABLE_COUNT=$(PGPASSWORD=$DB_PASSWORD psql \
  --host="$DB_HOST" \
  --port="$DB_PORT" \
  --username="$DB_USER" \
  --dbname="$DB_NAME" \
  --tuples-only \
  --command="
    SELECT COUNT(*) FROM information_schema.tables 
    WHERE table_schema = 'public';
  " | tr -d ' ')

echo -e "${BLUE}ℹ Tables in database: $TABLE_COUNT${NC}"

# Verify record counts for critical tables
echo ""
echo "Record counts:"
for table in users leads customers bookings payments followups; do
  COUNT=$(PGPASSWORD=$DB_PASSWORD psql \
    --host="$DB_HOST" \
    --port="$DB_PORT" \
    --username="$DB_USER" \
    --dbname="$DB_NAME" \
    --tuples-only \
    --command="SELECT COUNT(*) FROM $table WHERE is_deleted = false;" 2>/dev/null || echo "0")
  echo "  $table: $(echo $COUNT | tr -d ' ')"
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✓ Restore complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
