# Dead Letter Queue (DLQ) - Recovery & Operations Guide

## Overview

The Dead Letter Queue (DLQ) is a critical safety mechanism for data loss prevention in Celery task processing. Failed tasks are automatically captured and stored for manual intervention and retry, ensuring no work is lost.

**Architecture:**
- Failed tasks stored in Redis DB 5 (separate from task queue)
- Automatic retry mechanism: 3 attempts with exponential backoff
- Retention: 30 days (auto-cleanup)
- Monitoring: Prometheus metrics, Grafana dashboards, alerting
- Recovery: REST API for manual retry and bulk operations

---

## 1. How DLQ Works

### Task Processing Flow

```
Task Submitted
    ↓
Worker Receives → Executes
    ↓
Success → Result Stored (1h) → Cleaned Up
    ↓
Failure (Retry 1) → Wait 1m → Retry
    ↓
Failure (Retry 2) → Wait 2m → Retry
    ↓
Failure (Retry 3) → Wait 4m → Retry
    ↓
Failure (Final) → ADD TO DLQ ← Retained 30 days
```

### Automatic Error Handling

When a Celery task fails:

1. **Retry Logic** (3 attempts, exponential backoff):
   - Delay = base_delay × (2 ^ retry_count) + jitter
   - Delay range: 1m → 2m → 4m (max 10m)

2. **On Permanent Failure**:
   - Task stored in DLQ with:
     - Task ID, name, arguments
     - Error message, error type, full traceback
     - Retry count, timestamp
   - Alert sent to Slack/PagerDuty (if enabled)

3. **Retention & Cleanup**:
   - Auto-cleanup after 30 days
   - Manual cleanup available via API

---

## 2. DLQ API Reference

### 2.1 List Failed Tasks

**Endpoint**: `GET /api/v1/dlq/tasks`

**Query Parameters**:
- `limit` (int, default=50, max=500): Number of tasks to return
- `offset` (int, default=0): Pagination offset

**Example**:
```bash
curl "http://localhost:8000/api/v1/dlq/tasks?limit=20&offset=0"
```

**Response**:
```json
{
  "total": 5,
  "limit": 20,
  "offset": 0,
  "tasks": [
    {
      "task_id": "abc123def456",
      "task_name": "app.tasks.send_email",
      "error_message": "SMTP connection timeout",
      "error_type": "TimeoutError",
      "failed_at": "2026-08-01T10:30:00",
      "retry_count": 3
    }
  ]
}
```

### 2.2 Get Task Details

**Endpoint**: `GET /api/v1/dlq/tasks/{task_id}`

**Example**:
```bash
curl "http://localhost:8000/api/v1/dlq/tasks/abc123def456"
```

**Response**:
```json
{
  "task_id": "abc123def456",
  "task_name": "app.tasks.send_email",
  "args": "[user_id=123, email='user@example.com']",
  "kwargs": "{}",
  "error_message": "SMTP connection timeout",
  "error_type": "TimeoutError",
  "traceback": "Traceback (most recent call last):\n  File ...",
  "failed_at": "2026-08-01T10:30:00",
  "retry_count": 3
}
```

### 2.3 Retry Single Task

**Endpoint**: `POST /api/v1/dlq/tasks/{task_id}/retry`

**Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/dlq/tasks/abc123def456/retry"
```

**Response**:
```json
{
  "success": true,
  "message": "Task resubmitted for execution",
  "task_ids": ["abc123def456"]
}
```

**Flow**:
1. Task removed from DLQ
2. Task resubmitted to Celery queue
3. Worker processes task again
4. If fails: returned to DLQ after retries

### 2.4 Bulk Retry All Tasks

**Endpoint**: `POST /api/v1/dlq/tasks/retry-all`

**Query Parameters**:
- `task_name_filter` (string, optional): Filter by task name (partial match)
- `max_age_hours` (int, optional): Only retry tasks newer than this age

**Example**:
```bash
# Retry all failed email tasks from last 24 hours
curl -X POST "http://localhost:8000/api/v1/dlq/tasks/retry-all?task_name_filter=send_email&max_age_hours=24"
```

**Response**:
```json
{
  "success": true,
  "message": "5 tasks resubmitted for execution",
  "task_ids": ["abc123", "def456", "ghi789", "jkl012", "mno345"]
}
```

### 2.5 Delete Task from DLQ

**Endpoint**: `DELETE /api/v1/dlq/tasks/{task_id}`

**⚠️ WARNING**: Permanently deletes task. Use only for malformed data.

**Example**:
```bash
curl -X DELETE "http://localhost:8000/api/v1/dlq/tasks/abc123def456"
```

**Response**:
```json
{
  "success": "Task deleted from DLQ"
}
```

### 2.6 DLQ Statistics

**Endpoint**: `GET /api/v1/dlq/stats`

**Example**:
```bash
curl "http://localhost:8000/api/v1/dlq/stats"
```

**Response**:
```json
{
  "queue_depth": 5,
  "oldest_task_age_hours": 23.5,
  "retention_days": 30
}
```

### 2.7 Cleanup Old Tasks

**Endpoint**: `POST /api/v1/dlq/tasks/cleanup`

**Query Parameters**:
- `days_old` (int, default=30): Delete tasks older than this

**Example**:
```bash
# Manually cleanup tasks older than 30 days
curl -X POST "http://localhost:8000/api/v1/dlq/tasks/cleanup?days_old=30"
```

**Response**:
```json
{
  "deleted_count": 12,
  "message": "Deleted 12 tasks older than 30 days"
}
```

---

## 3. Monitoring DLQ Health

### 3.1 Prometheus Metrics

Available metrics (auto-scraped every 30 seconds):

```promql
# Queue depth (number of failed tasks)
dlq_queue_depth{environment="production"}

# Age of oldest task (hours)
dlq_oldest_task_age_hours{environment="production"}

# Tasks by type (breakdown)
dlq_task_by_type{task_name="app.tasks.send_email", environment="production"}

# Errors by type (breakdown)
dlq_error_by_type{error_type="TimeoutError", environment="production"}

# Task retry attempts
rate(dlq_retry_attempts_total[5m])
```

### 3.2 Grafana Dashboard

Create a dashboard with these panels:

**Panel 1: DLQ Queue Depth**
```promql
dlq_queue_depth
```
- Alert threshold: > 100 tasks (critical), > 10 tasks (warning)

**Panel 2: Oldest Task Age**
```promql
dlq_oldest_task_age_hours
```
- Alert threshold: > 24 hours (warning)

**Panel 3: Failed Tasks by Type**
```promql
dlq_task_by_type
```
- Shows breakdown of which task types are failing

**Panel 4: Errors by Type**
```promql
dlq_error_by_type
```
- Shows which error types are most common

### 3.3 Alert Rules

Configured in `monitoring/alert_rules.yml`:

| Alert | Condition | Severity |
|-------|-----------|----------|
| `DLQQueueNotEmpty` | queue_depth > 0 | Warning (2m) |
| `HighDLQQueueDepth` | queue_depth > 100 | Critical (5m) |
| `OldTasksInDLQ` | oldest_task_age > 24h | Warning (5m) |

---

## 4. Incident Response Procedures

### Scenario 1: Single Failed Task

**Detection**: Alert or manual check shows 1 task in DLQ

**Investigation**:
```bash
# 1. Get task details
curl "http://localhost:8000/api/v1/dlq/tasks/{task_id}"

# 2. Review error and traceback
# 3. Identify root cause
```

**Resolution**:

**Option A - Simple Retry** (if transient error):
```bash
# Retry the task
curl -X POST "http://localhost:8000/api/v1/dlq/tasks/{task_id}/retry"

# Monitor if it succeeds
# If fails again: added back to DLQ
```

**Option B - Fix & Retry** (if code issue):
1. Fix code issue in application
2. Deploy fix
3. Retry task: `curl -X POST "http://localhost:8000/api/v1/dlq/tasks/{task_id}/retry"`

**Option C - Delete** (if data invalid/malformed):
```bash
# Delete if task cannot be fixed
curl -X DELETE "http://localhost:8000/api/v1/dlq/tasks/{task_id}"

# Document why it was deleted (for audit)
```

---

### Scenario 2: Multiple Tasks of Same Type

**Detection**: Dashboard shows 50 `send_email` tasks in DLQ

**Investigation**:
```bash
# 1. Check common error
curl "http://localhost:8000/api/v1/dlq/tasks" | jq '.tasks[] | select(.task_name=="app.tasks.send_email")'

# 2. Review logs for pattern
docker logs rpex_backend | grep "send_email.*error"

# 3. Check external dependency status
# - SMTP server availability
# - Email provider API status
# - Network connectivity
```

**Resolution**:

**If temporary outage** (e.g., SMTP down):
```bash
# 1. Wait for service recovery
# 2. Retry all email tasks
curl -X POST "http://localhost:8000/api/v1/dlq/tasks/retry-all?task_name_filter=send_email"
```

**If configuration issue** (e.g., wrong credentials):
```bash
# 1. Fix configuration
# 2. Restart backend service
docker-compose restart backend

# 3. Retry tasks
curl -X POST "http://localhost:8000/api/v1/dlq/tasks/retry-all?task_name_filter=send_email"
```

**If code bug** (e.g., email parsing):
```bash
# 1. Fix bug in app/tasks/email.py
# 2. Deploy new version
# 3. Retry tasks
curl -X POST "http://localhost:8000/api/v1/dlq/tasks/retry-all?task_name_filter=send_email"

# 4. Verify success rate
curl "http://localhost:8000/api/v1/dlq/stats"
```

---

### Scenario 3: DLQ Queue Growing Rapidly

**Detection**: Alert `HighDLQQueueDepth` (> 100 tasks) fires

**Investigation**:
```bash
# 1. Get current stats
curl "http://localhost:8000/api/v1/dlq/stats"

# 2. Check error breakdown
curl "http://localhost:8000/api/v1/dlq/tasks?limit=500" | jq '.tasks | group_by(.error_type) | map({type: .[0].error_type, count: length})'

# 3. Check application health
curl "http://localhost:8000/health"

# 4. Check worker status
docker logs rpex_celery_worker | tail -100

# 5. Check external dependencies
# - Database availability
# - Redis availability
# - External API availability
```

**Resolution**:

**If systemic issue** (e.g., database down):
1. Restore the failing dependency
2. Wait for workers to recover
3. Monitor DLQ stats: `curl "http://localhost:8000/api/v1/dlq/stats"`
4. DLQ should decrease as workers process queued tasks

**If worker issue** (e.g., OOM, crash):
1. Check worker logs: `docker logs rpex_celery_worker`
2. Restart workers: `docker-compose restart celery-worker`
3. Monitor: `docker ps | grep celery`

**If external API issue** (e.g., rate limiting):
1. Identify failing task type
2. Check external service status
3. Implement rate limiting in code if needed
4. Wait for throttling to reset
5. Bulk retry: `curl -X POST "http://localhost:8000/api/v1/dlq/tasks/retry-all"`

---

### Scenario 4: Tasks Stuck in DLQ for Days

**Detection**: Alert `OldTasksInDLQ` (> 24 hours) fires

**Investigation**:
```bash
# 1. List oldest tasks
curl "http://localhost:8000/api/v1/dlq/tasks?limit=10&offset=0" | jq '.tasks[] | {task_id, task_name, failed_at}'

# 2. Get details of oldest task
curl "http://localhost:8000/api/v1/dlq/tasks/{oldest_task_id}"

# 3. Check if similar tasks are still failing
curl "http://localhost:8000/api/v1/dlq/tasks?limit=100" | jq '.tasks | map(.task_name) | group_by(.) | map({name: .[0], count: length})'
```

**Resolution**:

**Option A - Retry if cause is resolved**:
```bash
# If underlying issue is fixed, retry all old tasks
curl -X POST "http://localhost:8000/api/v1/dlq/tasks/retry-all?max_age_hours=48"

# Monitor results
curl "http://localhost:8000/api/v1/dlq/stats"
```

**Option B - Clean up if unrecoverable**:
```bash
# Cleanup very old tasks (older than 30 days)
curl -X POST "http://localhost:8000/api/v1/dlq/tasks/cleanup?days_old=30"

# Document in incident report
```

**Option C - Selective deletion**:
```bash
# Review each task manually
for task_id in $(curl "http://localhost:8000/api/v1/dlq/tasks" | jq -r '.tasks[].task_id'); do
  # Review details
  curl "http://localhost:8000/api/v1/dlq/tasks/$task_id"
  
  # Delete if unrecoverable
  curl -X DELETE "http://localhost:8000/api/v1/dlq/tasks/$task_id"
done
```

---

## 5. Best Practices

### Proactive Monitoring

1. **Daily Review**:
   ```bash
   # Check DLQ health daily
   curl "http://localhost:8000/api/v1/dlq/stats"
   
   # Alert if > 5 tasks
   ```

2. **Weekly Audit**:
   ```bash
   # Review all tasks in DLQ
   curl "http://localhost:8000/api/v1/dlq/tasks?limit=1000"
   
   # Group by error type
   # Identify patterns
   ```

3. **Monthly Cleanup**:
   ```bash
   # Remove tasks older than 30 days
   curl -X POST "http://localhost:8000/api/v1/dlq/tasks/cleanup?days_old=30"
   ```

### Task Design

1. **Idempotency**: Design tasks to be safely retried
   ```python
   @celery.task(bind=True)
   def send_email(self, user_id):
       # Check if already sent (idempotent)
       if EmailLog.objects.filter(user_id=user_id, sent_at=today).exists():
           return  # Already sent today, skip
       
       # Send email
       ...
   ```

2. **Timeout Configuration**: Set reasonable timeouts
   ```python
   @celery.task(bind=True, time_limit=300, soft_time_limit=250)
   def long_running_task(self):
       try:
           # Do work
           ...
       except SoftTimeLimitExceeded:
           # Cleanup
           logger.warning("Task timeout")
           raise
   ```

3. **Error Handling**: Log before failing
   ```python
   @celery.task(bind=True)
   def process_data(self, data):
       try:
           # Process
           ...
       except ValueError as e:
           logger.error(f"Invalid data: {e}", extra={"data": data})
           raise  # Will be retried or go to DLQ
   ```

### Alerting Strategy

Configure alerting in Slack:

```yaml
# alertmanager.yml
routes:
  - match:
      alertname: "DLQQueueNotEmpty"
    receiver: "dlq_channel"
    group_wait: 5m

receivers:
  - name: "dlq_channel"
    slack_configs:
      - channel: "#alerts"
        title: "DLQ Task Failed"
        text: "{{ .GroupLabels.task_name }} - Check /api/v1/dlq/tasks"
```

---

## 6. Integration Examples

### 6.1 Slack Bot Command

Create a Slash command to check DLQ:

```python
@app.post("/slack/commands/dlq")
async def dlq_slack_command(request: Request):
    """Slash command: /dlq-stats"""
    data = await request.form()
    
    # Get DLQ stats
    stats = dlq_manager.get_dlq_stats()
    
    # Format Slack message
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*DLQ Status*\nQueue Depth: {stats['queue_depth']}\nOldest Task: {stats['oldest_task_age_hours']:.1f}h"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "View Tasks"},
                    "url": "http://localhost:3001/d/dlq-dashboard"
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Retry All"},
                    "action_id": "retry_all_dlq"
                }
            ]
        }
    ]
    
    return {"response_type": "in_channel", "blocks": blocks}
```

### 6.2 Automated Recovery Script

```bash
#!/bin/bash
# scripts/dlq-recovery.sh

DLQ_API="http://localhost:8000/api/v1/dlq"
SLACK_WEBHOOK="$SLACK_WEBHOOK_URL"

# Check if DLQ has tasks
STATS=$(curl -s "$DLQ_API/stats")
QUEUE_DEPTH=$(echo $STATS | jq '.queue_depth')

if [ $QUEUE_DEPTH -gt 100 ]; then
    echo "Critical: $QUEUE_DEPTH tasks in DLQ"
    
    # Get top error types
    ERRORS=$(curl -s "$DLQ_API/tasks?limit=100" | jq '[.tasks[].error_type] | group_by(.) | map({error: .[0], count: length}) | sort_by(.count) | reverse')
    
    # Notify Slack
    curl -X POST $SLACK_WEBHOOK -H 'Content-type: application/json' \
        -d "{\"text\": \"🚨 DLQ Critical: $QUEUE_DEPTH tasks failed\n\`\`\`$ERRORS\`\`\`\"}"
    
    # Auto-retry if recent tasks
    curl -X POST "$DLQ_API/tasks/retry-all?max_age_hours=1"
fi
```

---

## 7. Troubleshooting

### Problem: Tasks not appearing in DLQ

**Check:**
1. Is Redis DB 5 accessible?
   ```bash
   redis-cli -n 5 ping
   ```

2. Is DLQ manager initialized?
   ```bash
   # Check logs
   docker logs rpex_backend | grep -i dlq
   ```

3. Are tasks actually failing?
   ```bash
   docker logs rpex_celery_worker | grep -i error
   ```

### Problem: DLQ metrics not updating

**Check:**
1. Is metrics endpoint working?
   ```bash
   curl http://localhost:8000/metrics | grep dlq_
   ```

2. Is background task running?
   ```bash
   # Check application logs
   docker logs rpex_backend | grep "DLQ metrics"
   ```

3. Enable debug logging:
   ```python
   # app/core/logging.py
   logger.enable("app.metrics.dlq_metrics")
   ```

### Problem: Retry fails with "Task not found"

**Cause**: Task was already removed or DLQ Redis connection failed

**Fix**:
1. Verify Redis DB 5 is accessible
2. Check if task was already retried
3. Verify Redis storage has capacity

---

## 8. SLA & Recovery Targets

| Scenario | RTO | RPO | Action |
|----------|-----|-----|--------|
| Single task fails | 1h | 0 | Manual retry via API |
| Multiple tasks fail | 2h | 0 | Investigate & bulk retry |
| DLQ queue depth > 100 | 30m | 0 | Escalate to on-call |
| Tasks stuck > 24h | 4h | 0 | Manual review & cleanup |
| Redis DB 5 down | 15m | 1h | Failover or restart |

---

## Support & Escalation

**On-call Engineer**:
- DLQ alert fires
- Review Grafana dashboard
- Check `/api/v1/dlq/stats`
- Follow incident response procedures

**Escalation**:
- Systemic failures (100+ tasks) → Page platform team
- External API issues → Contact vendor
- Data loss risk → Escalate to CTO

**Runbook**: This document  
**Dashboard**: Grafana → DLQ Dashboard  
**Metrics**: Prometheus → http://localhost:9090  
**Logs**: `docker logs rpex_celery_worker`

