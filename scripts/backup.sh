#!/bin/bash
# Database Backup Script for RPEX CRM PostgreSQL
# Usage: ./backup.sh [staging|production]
# Backs up PostgreSQL database to timestamped SQL file and optionally to S3

set -e

ENVIRONMENT=${1:-staging}
DB_USER=${DB_USER:-rpex}
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-rpex_crm}
BACKUP_DIR="./backups"
RETENTION_DAYS=${RETENTION_DAYS:-30}

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Generate timestamped filename
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${ENVIRONMENT}_${TIMESTAMP}.sql.gz"
BACKUP_LOG="$BACKUP_DIR/${DB_NAME}_${ENVIRONMENT}_${TIMESTAMP}.log"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 RPEX CRM Database Backup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Environment: $ENVIRONMENT"
echo "Database: $DB_NAME @ $DB_HOST:$DB_PORT"
echo "Backup File: $BACKUP_FILE"
echo "Timestamp: $TIMESTAMP"
echo ""

# Perform backup
echo "⏳ Starting backup..."
if PGPASSWORD=$DB_PASSWORD pg_dump \
  --host="$DB_HOST" \
  --port="$DB_PORT" \
  --username="$DB_USER" \
  --dbname="$DB_NAME" \
  --format=plain \
  --compress=9 \
  --no-owner \
  --no-acl \
  2>"$BACKUP_LOG" | tee "$BACKUP_FILE" > /dev/null; then
  
  BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
  echo -e "${GREEN}✓ Backup successful!${NC}"
  echo "  File: $BACKUP_FILE"
  echo "  Size: $BACKUP_SIZE"
else
  echo -e "${RED}✗ Backup failed!${NC}"
  cat "$BACKUP_LOG"
  exit 1
fi

# Upload to S3 if configured
if [ ! -z "$AWS_S3_BUCKET" ]; then
  echo ""
  echo "⏳ Uploading to S3..."
  if aws s3 cp "$BACKUP_FILE" "s3://$AWS_S3_BUCKET/database-backups/$ENVIRONMENT/$BACKUP_FILE"; then
    echo -e "${GREEN}✓ S3 upload successful!${NC}"
    echo "  Location: s3://$AWS_S3_BUCKET/database-backups/$ENVIRONMENT/$BACKUP_FILE"
  else
    echo -e "${YELLOW}⚠ S3 upload failed (backup saved locally)${NC}"
  fi
fi

# Cleanup old backups (local)
echo ""
echo "⏳ Cleaning up old backups (retention: $RETENTION_DAYS days)..."
DELETED_COUNT=0
while IFS= read -r old_file; do
  rm -f "$old_file"
  ((DELETED_COUNT++))
done < <(find "$BACKUP_DIR" -name "${DB_NAME}_${ENVIRONMENT}_*.sql.gz" -mtime +"$RETENTION_DAYS")

if [ $DELETED_COUNT -gt 0 ]; then
  echo -e "${GREEN}✓ Deleted $DELETED_COUNT old backup(s)${NC}"
fi

# Cleanup old S3 backups
if [ ! -z "$AWS_S3_BUCKET" ]; then
  echo ""
  echo "⏳ Cleaning up old S3 backups..."
  # Note: S3 cleanup requires AWS CLI and proper IAM permissions
  aws s3 ls "s3://$AWS_S3_BUCKET/database-backups/$ENVIRONMENT/" | while read -r line; do
    createdate=$(echo $line | awk {'print $1" "$2'})
    createdate=$(date -d "$createdate" +%s)
    olderdate=$(date --date "$RETENTION_DAYS days ago" +%s)
    if [ $createdate -lt $olderdate ]; then
      key=$(echo $line | awk {'print $4'})
      if [ ! -z "$key" ]; then
        aws s3 rm "s3://$AWS_S3_BUCKET/database-backups/$ENVIRONMENT/$key"
      fi
    fi
  done
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✓ Backup complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
