# RPEX CRM Database Backup Strategy

## Overview

Comprehensive backup and disaster recovery strategy for RPEX CRM PostgreSQL database, ensuring business continuity and data protection.

---

## 1. Backup Strategy

### 1.1 Backup Types

#### Full Backup (Daily)
- **Frequency**: Every day at 02:00 UTC
- **Method**: `pg_dump` with full schema and data
- **Retention**: 30 days
- **Size**: ~50-200 MB (compressed)
- **Time to Complete**: 5-15 minutes

#### Incremental Backup (Hourly via WAL)
- **Frequency**: Every hour
- **Method**: PostgreSQL Write-Ahead Logs (WAL) archiving
- **Retention**: 7 days
- **Size**: ~10-50 MB per hour
- **Enables**: Point-in-time recovery (PITR)

#### On-Demand Backup (Before Critical Operations)
- **Frequency**: Manually before deployments, major updates
- **Method**: Full backup
- **Retention**: 90 days (archived)
- **Process**: Execute `./scripts/backup.sh production`

### 1.2 Backup Destinations

#### Primary (Local)
- Location: `/backups/` (mounted volume in production)
- Retention: 30 days
- Purpose: Quick recovery, immediate access

#### Secondary (Cloud - AWS S3)
- Location: `s3://rpex-backups/database-backups/production/`
- Retention: 90 days (lifecycle policy)
- Purpose: Disaster recovery, geographic redundancy
- Encryption: AES-256, server-side

#### Tertiary (Offline Archive)
- Quarterly snapshots to external drive
- Monthly backups to AWS Glacier Deep Archive
- Purpose: Compliance, long-term retention

---

## 2. Backup Implementation

### 2.1 Automated Daily Backup (Cron)

Add to production server crontab:

```bash
# Daily backup at 02:00 UTC
0 2 * * * /opt/rpex-crm/scripts/backup.sh production >> /var/log/rpex/backup.log 2>&1

# Verify backup integrity every Sunday
0 3 * * 0 /opt/rpex-crm/scripts/verify-backup.sh production >> /var/log/rpex/backup-verify.log 2>&1
```

### 2.2 Environment Variables

```bash
# .env or systemd service file
DB_USER=rpex_prod
DB_HOST=postgres.example.com
DB_PORT=5432
DB_NAME=rpex_crm_prod
DB_PASSWORD=<secure-password>
BACKUP_DIR=/backups
RETENTION_DAYS=30
AWS_S3_BUCKET=rpex-backups
AWS_REGION=us-east-1
```

### 2.3 Usage

**Immediate backup (before deployment):**
```bash
./scripts/backup.sh production
```

**Scheduled backup (cron job):**
```bash
0 2 * * * /path/to/backup.sh production
```

**Restore from backup:**
```bash
./scripts/restore.sh ./backups/rpex_crm_production_20260801_020000.sql.gz
```

---

## 3. Write-Ahead Logs (WAL) Configuration

### 3.1 Enable WAL Archiving

PostgreSQL configuration (`postgresql.conf`):

```ini
# Enable archiving
wal_level = replica                    # Required for WAL archiving
archive_mode = on
archive_command = 'test ! -f /mnt/wal-archive/%f && cp %p /mnt/wal-archive/%f'
archive_timeout = 300                 # Archive every 5 minutes
```

Or with S3 (using pgBackRest):

```bash
# Install pgBackRest
apt-get install pgbackrest

# Configuration (/etc/pgbackrest/pgbackrest.conf)
[global]
repo1-type=s3
repo1-s3-bucket=rpex-wal-archive
repo1-s3-key=<AWS_ACCESS_KEY>
repo1-s3-key-secret=<AWS_SECRET_KEY>
repo1-s3-region=us-east-1

[stanza:rpex_crm]
pg1-path=/var/lib/postgresql/16/main
```

### 3.2 Recovery Configuration

For point-in-time recovery, PostgreSQL needs recovery configuration:

```bash
# Create recovery configuration
cat > /var/lib/postgresql/16/main/recovery.conf << EOF
restore_command = 'cp /mnt/wal-archive/%f %p'
recovery_target_timeline = 'latest'
recovery_target_name = 'before_bad_migration'  # Named savepoint
EOF

# Or with timestamp
recovery_target_time = '2026-08-01 12:30:00'
```

---

## 4. Restore Procedures

### 4.1 Full Restore (from daily backup)

```bash
# 1. Stop application
systemctl stop rpex-backend rpex-celery

# 2. Run restore script (interactive)
./scripts/restore.sh ./backups/rpex_crm_production_20260801_020000.sql.gz

# 3. Run migrations to ensure schema is up-to-date
cd backend
alembic upgrade head

# 4. Restart application
systemctl start rpex-backend rpex-celery

# 5. Verify application health
curl http://localhost:8000/health
```

### 4.2 Point-in-Time Recovery (PITR)

```bash
# 1. Stop PostgreSQL
sudo systemctl stop postgresql

# 2. Restore base backup
cd /var/lib/postgresql/16/main
rm -rf *
pg_basebackup -D . -h backup.s3.example.com -R

# 3. Create recovery configuration
cat > recovery.conf << EOF
restore_command = 'aws s3 cp s3://rpex-wal-archive/%f %p'
recovery_target_time = '2026-08-01 14:30:00 UTC'
recovery_target_timeline = 'latest'
EOF

# 4. Start PostgreSQL (will run recovery)
sudo systemctl start postgresql

# 5. Monitor recovery progress
tail -f /var/log/postgresql/postgresql.log

# 6. Verify data integrity once recovery completes
sudo -u postgres psql -d rpex_crm_prod -c "SELECT COUNT(*) FROM users;"
```

### 4.3 Cross-Region Disaster Recovery

```bash
# On disaster recovery server (different region)

# 1. Download backup from S3
aws s3 cp s3://rpex-backups/database-backups/production/rpex_crm_production_20260801_020000.sql.gz .

# 2. Create database
sudo -u postgres createdb rpex_crm_prod

# 3. Restore
gunzip -c rpex_crm_production_20260801_020000.sql.gz | sudo -u postgres psql -d rpex_crm_prod

# 4. Update connection strings in application
export DATABASE_URL=postgresql://rpex_prod:password@dr-postgres.example.com:5432/rpex_crm_prod

# 5. Restart application
docker-compose -f docker-compose.prod.yml up -d
```

---

## 5. Backup Verification

### 5.1 Automatic Verification (Weekly)

Create `scripts/verify-backup.sh`:

```bash
#!/bin/bash
# Verify backup integrity by restoring to temporary database

BACKUP_FILE="$1"
DB_USER=rpex_test
DB_HOST=localhost
DB_NAME=rpex_crm_test_restore

echo "Verifying backup: $BACKUP_FILE"

# Drop test database if exists
PGPASSWORD=$DB_PASSWORD psql -U postgres -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;" 2>/dev/null || true

# Create test database
PGPASSWORD=$DB_PASSWORD psql -U postgres -d postgres -c "CREATE DATABASE $DB_NAME;"

# Restore to test database
if gunzip -c "$BACKUP_FILE" | PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -d $DB_NAME 2>/dev/null; then
  # Run integrity checks
  TABLES=$(PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';")
  USERS=$(PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM users WHERE is_deleted=false;")
  
  echo "✓ Backup verified successfully"
  echo "  Tables: $TABLES"
  echo "  Active users: $USERS"
  
  # Cleanup
  PGPASSWORD=$DB_PASSWORD psql -U postgres -d postgres -c "DROP DATABASE $DB_NAME;"
  exit 0
else
  echo "✗ Backup verification failed"
  exit 1
fi
```

### 5.2 Manual Verification

```bash
# Check backup file size
ls -lh ./backups/rpex_crm_production_*.sql.gz

# Test restore on staging environment
./scripts/restore.sh ./backups/rpex_crm_production_20260801_020000.sql.gz

# Run application tests
pytest backend/tests -v

# Verify data consistency
psql -c "SELECT COUNT(*) FROM leads WHERE budget_min > budget_max;"  # Should be 0
```

---

## 6. Monitoring & Alerting

### 6.1 Backup Status Monitoring

Create a health check endpoint:

```python
# backend/app/api/v1/monitoring.py

@router.get("/backup-status", tags=["monitoring"])
async def get_backup_status():
    """Check backup status and report to monitoring system."""
    
    backup_dir = "/backups"
    now = datetime.now()
    threshold = timedelta(days=1.5)  # Alert if no backup in 36 hours
    
    # Find latest backup
    latest_backup = max(
        glob.glob(f"{backup_dir}/rpex_crm_production_*.sql.gz"),
        key=os.path.getctime,
        default=None
    )
    
    if not latest_backup:
        return {
            "status": "critical",
            "message": "No backup found",
            "last_backup": None
        }
    
    last_backup_time = datetime.fromtimestamp(os.path.getctime(latest_backup))
    age = now - last_backup_time
    
    if age > threshold:
        return {
            "status": "warning",
            "message": f"Backup is {age.days}d old",
            "last_backup": last_backup_time.isoformat(),
            "age_hours": age.total_seconds() / 3600
        }
    
    return {
        "status": "healthy",
        "message": "Recent backup available",
        "last_backup": last_backup_time.isoformat(),
        "age_hours": age.total_seconds() / 3600,
        "file": os.path.basename(latest_backup)
    }
```

### 6.2 Alerting Rules (Prometheus)

Create `monitoring/prometheus-rules.yml`:

```yaml
groups:
  - name: database_backup
    rules:
      - alert: NoBackupIn24Hours
        expr: time() - backup_timestamp_seconds > 86400
        for: 15m
        annotations:
          summary: "No database backup in 24 hours"
          description: "Last backup: {{ $value | humanizeDuration }} ago"
          
      - alert: BackupSizeTooSmall
        expr: backup_size_bytes < 5000000  # 5MB
        for: 10m
        annotations:
          summary: "Database backup is suspiciously small"
          description: "Size: {{ $value | humanize }}B"
          
      - alert: WALArchivingFailed
        expr: increase(postgres_wal_archive_failed_total[5m]) > 0
        annotations:
          summary: "PostgreSQL WAL archiving failed"
```

---

## 7. Disaster Recovery Plan

### 7.1 RTO/RPO Targets

| Scenario | RTO | RPO |
|----------|-----|-----|
| Data corruption (single table) | 1 hour | 1 hour |
| Database crash | 2 hours | 30 minutes |
| Server failure | 4 hours | 1 hour |
| Data center outage | 8 hours | 4 hours |

### 7.2 Runbook: Database Corruption

1. **Identify** the corrupted data (check application error logs)
2. **Alert** the team (page on-call)
3. **Stop** the application (`systemctl stop rpex-*`)
4. **Restore** point-in-time backup to 30 min before corruption:
   ```bash
   ./scripts/restore.sh backup_before_corruption.sql.gz
   alembic upgrade head
   ```
5. **Verify** data integrity
6. **Restart** application
7. **Monitor** for issues
8. **Post-incident** review

### 7.3 Runbook: Server Failure

1. **Provision** new server (same specs)
2. **Install** PostgreSQL + dependencies
3. **Restore** latest backup from S3:
   ```bash
   aws s3 cp s3://rpex-backups/latest.sql.gz .
   ./scripts/restore.sh latest.sql.gz
   ```
4. **Update** DNS/load balancer to point to new server
5. **Restart** application services
6. **Verify** connectivity and data
7. **Archive** old server (after 24h verification)

---

## 8. Backup Checklist

- [ ] Daily automated backups running on schedule
- [ ] Backup files stored on local volume
- [ ] Backups uploaded to S3 with encryption
- [ ] Retention policies enforced (30 days local, 90 days S3)
- [ ] WAL archiving enabled and tested
- [ ] Backup verification running weekly
- [ ] Restore procedures tested monthly
- [ ] PITR recovery tested quarterly
- [ ] Backup status monitoring alert active
- [ ] Team trained on restore procedures
- [ ] Documentation updated
- [ ] Off-site backups (Glacier) scheduled

---

## 9. Compliance & Regulatory

- **GDPR**: Data residency, right to erasure (backups deleted after retention)
- **ISO 27001**: Backup encryption, access controls, audit logs
- **SOC 2**: Backup testing, incident response, disaster recovery drills

Maintain audit trail of all backup operations in `backup.log`.

---

## Support & Escalation

- **Backup failures**: On-call engineer, Page within 15 min
- **Restore requests**: Can take up to 4 hours depending on size
- **Production incidents**: Follow incident response playbook
- **Quarterly drills**: Scheduled restore tests to verify procedures

