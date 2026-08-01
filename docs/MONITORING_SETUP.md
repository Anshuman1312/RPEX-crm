# RPEX CRM Monitoring & Alerting Setup Guide

## Overview

Complete monitoring and alerting infrastructure for RPEX CRM using Prometheus, Grafana, Alertmanager, and various exporters.

**Components:**
- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **Alertmanager**: Alert routing and notifications
- **Exporters**: PostgreSQL, Redis, Node, Nginx

---

## 1. Quick Start

### 1.1 Deploy Monitoring Stack

```bash
# Create monitoring namespace
docker network create rpex_network

# Start monitoring services
docker-compose -f monitoring/docker-compose.monitoring.yml up -d

# Verify all services are running
docker ps | grep rpex_

# Access dashboards
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3001
# - Alertmanager: http://localhost:9093
```

### 1.2 Configure Environment Variables

Add to `.env`:

```bash
# Prometheus
PROMETHEUS_RETENTION_DAYS=30

# Grafana
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=<generate-secure-password>
GRAFANA_URL=http://localhost:3001

# Alertmanager
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
PAGERDUTY_SERVICE_KEY=<your-pagerduty-key>

# Email notifications
ALERT_EMAIL_CRITICAL=oncall@company.com
ALERT_EMAIL_WARNING=devops@company.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=alerts@company.com
SMTP_PASSWORD=<app-password>
```

---

## 2. Prometheus Setup

### 2.1 Configuration

File: `monitoring/prometheus.yml`

Scrapes metrics from:
- **FastAPI** (`/metrics`): HTTP requests, errors, latency
- **PostgreSQL** (port 9187): Query performance, connections, disk
- **Redis** (port 9121): Memory, keys, evictions
- **Node** (port 9100): CPU, memory, disk, network
- **Nginx** (port 9113): Requests, latency, connections

### 2.2 Data Retention

Default: 30 days at 15s resolution

For production, consider:
```bash
# 90 days retention (requires ~50GB storage)
docker run -e 'PROMETHEUS_STORAGE_RETENTION=2160h' ...

# Or use remote storage (Thanos, S3)
# See: https://prometheus.io/docs/prometheus/latest/storage/#remote-storage-integrations
```

### 2.3 Verify Scraping

Check Prometheus UI:
1. Navigate to http://localhost:9090/targets
2. Verify all targets are "UP" (green)
3. Each exporter should show "State: UP"

If a target is DOWN:
```bash
# Check if exporter is running
docker ps | grep rpex_

# Check logs
docker logs rpex_<exporter_name>

# Verify network connectivity
docker exec rpex_prometheus curl http://<exporter>:9xxx/metrics
```

---

## 3. Alert Rules

### 3.1 Alert Severity Levels

| Severity | Response | Examples |
|----------|----------|----------|
| **critical** | Immediate (5 min) | DB down, 0 workers, error rate >50% |
| **warning** | Soon (30 min) | CPU 80%, slow queries, queue depth 1000+ |
| **info** | Background | Slow logs, backup complete, config change |

### 3.2 Alert Configuration

File: `monitoring/alert_rules.yml`

Key alert categories:
1. **Application Health**: Error rate, response time, request queue
2. **Database**: Connectivity, pool exhaustion, slow queries, disk space
3. **Cache**: Redis down, memory usage, evictions
4. **Tasks**: Celery workers, failure rate, stuck tasks
5. **System**: CPU, memory, disk, load average
6. **Backup**: Missing backups, WAL archiving

### 3.3 Test Alert

Manually trigger an alert in Prometheus:

```bash
# Port-forward to Prometheus
kubectl port-forward svc/prometheus 9090:9090

# Navigate to http://localhost:9090/alerts
# Find a rule and click "Show Graph"
# Manually trigger by modifying thresholds

# Or use Docker
curl 'http://localhost:9090/api/v1/query?query=up{job="rpex-backend"}'
```

---

## 4. Alertmanager Setup

### 4.1 Notification Routing

File: `monitoring/alertmanager.yml`

Three-tier routing:
- **Critical** → PagerDuty + Slack #incidents + SMS
- **Warning** → Slack #alerts + Email
- **Info** → Slack #monitoring only

### 4.2 Slack Integration

1. Create Slack App: https://api.slack.com/apps
2. Enable "Incoming Webhooks"
3. Create webhook for #incidents, #alerts, #monitoring
4. Add to `.env`:
   ```bash
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00/B00/XX
   ```

### 4.3 PagerDuty Integration

1. Create service in PagerDuty
2. Add "Prometheus" integration
3. Get integration key
4. Add to `.env`:
   ```bash
   PAGERDUTY_SERVICE_KEY=xyz
   ```

### 4.4 Email Alerts

1. Set SMTP credentials in `.env`
2. Use Gmail App Password (not regular password):
   - Account Settings → Security → App passwords
   - Generate password for "Mail" and "Windows"
   - Use in `SMTP_PASSWORD`

### 4.5 Testing Notifications

```bash
# Create manual alert in Alertmanager
curl -X POST http://localhost:9093/api/v1/alerts -H "Content-Type: application/json" -d '[{
  "labels": {
    "alertname": "TestAlert",
    "severity": "critical"
  },
  "annotations": {
    "description": "This is a test alert"
  }
}]'

# Check Slack and email for notifications
```

---

## 5. Grafana Dashboards

### 5.1 Pre-built Dashboards

Import community dashboards:

1. **Application Dashboard** (ID: 3662)
   - FastAPI metrics, request rates, error rates
   
2. **PostgreSQL Dashboard** (ID: 9628)
   - Query performance, connections, cache hit ratio
   
3. **Redis Dashboard** (ID: 11835)
   - Memory usage, keys, evictions, commands
   
4. **System Dashboard** (ID: 1860)
   - CPU, memory, disk, network, load

To import:
1. Grafana → Dashboards → Import
2. Enter dashboard ID or paste JSON
3. Select Prometheus data source
4. Click Import

### 5.2 Custom Dashboards

Create custom dashboard: `monitoring/grafana/dashboards/rpex-crm-overview.json`

Key panels:
- **Application**: Error rate, latency, throughput, active requests
- **Database**: Connection pool, slow queries, disk usage, cache ratio
- **Cache**: Hit rate, memory, evictions, commands/sec
- **Tasks**: Worker count, task rate, failure rate, queue depth
- **Infrastructure**: CPU, memory, disk, network utilization

### 5.3 Alert Preview in Grafana

Dashboard panels can show alert status:
```json
{
  "fieldConfig": {
    "defaults": {
      "custom": {
        "hideFrom": {
          "tooltip": false,
          "viz": false,
          "legend": false
        }
      }
    }
  },
  "targets": [
    {
      "expr": "ALERTS{alertname='HighErrorRate'}",
      "refId": "A"
    }
  ]
}
```

---

## 6. Key Metrics to Monitor

### Application Metrics

```promql
# Error rate
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# P95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Active connections
http_requests_pending

# Requests per second
rate(http_requests_total[1m])
```

### Database Metrics

```promql
# Connection pool usage
pg_stat_activity_count / pg_settings_max_connections

# Slow query detection
rate(pg_stat_statements_mean_exec_time[5m]) > 1000

# Disk usage
pg_database_size_bytes / 1024 / 1024 / 1024

# Cache hit ratio
1 - (pg_stat_database_blks_read / (pg_stat_database_blks_read + pg_stat_database_blks_hit))
```

### Redis Metrics

```promql
# Memory usage percentage
redis_memory_used_bytes / redis_memory_max_bytes

# Cache hit rate
redis_keyspace_hits_total / (redis_keyspace_hits_total + redis_keyspace_misses_total)

# Connected clients
redis_connected_clients

# Evictions
rate(redis_evicted_keys_total[5m])
```

### Celery Task Metrics

```promql
# Task success rate
rate(celery_task_succeeded_total[5m]) / (rate(celery_task_succeeded_total[5m]) + rate(celery_task_failed_total[5m]))

# Worker count
count(celery_worker_tasks_active)

# Queue depth
celery_queue_length
```

---

## 7. Runbooks (Alert Response)

### HighErrorRate

**Alert:** Error rate > 5% for 5 minutes

**Investigation:**
1. Check Grafana application dashboard
2. Identify which endpoints have high errors
3. Check backend logs: `docker logs rpex_backend`
4. Look for specific error patterns

**Resolution:**
- If code issue: Deploy fix with rollback plan
- If database issue: Check PostgreSQL status
- If external API: Check third-party status pages

### PostgreSQLDown

**Alert:** Database unreachable for 2 minutes

**Investigation:**
1. Check PostgreSQL container status: `docker ps | grep postgres`
2. Check logs: `docker logs rpex_postgres`
3. Verify network connectivity: `docker exec rpex_backend pg_isready -h postgres`
4. Check disk space: `docker exec rpex_postgres df -h`

**Resolution:**
- Restart container: `docker restart rpex_postgres`
- Restore from backup if corrupted: `./scripts/restore.sh <backup_file>`
- Page on-call DBA

### RedisDown

**Alert:** Redis unreachable for 2 minutes

**Investigation:**
1. Check Redis container: `docker ps | grep redis`
2. Check logs: `docker logs rpex_redis`
3. Verify connectivity: `redis-cli ping`
4. Check memory: `redis-cli info memory`

**Resolution:**
- Restart Redis: `docker restart rpex_redis` (temporary cache loss)
- Clear expired keys: `redis-cli EVAL "return redis.call('del', unpack(redis.call('keys', ARGV[1])))" 0 '*'"`
- Increase memory if near limit

### CeleryWorkerDown

**Alert:** No active Celery workers for 2 minutes

**Investigation:**
1. Check worker status: `docker ps | grep celery`
2. Check logs: `docker logs rpex_celery_worker`
3. Check broker connectivity: `redis-cli -n 3 ping` (DB 3 is Celery DB)
4. Look for exceptions in logs

**Resolution:**
- Restart worker: `docker restart rpex_celery_worker`
- Check Redis Celery DB: `redis-cli -n 3 llen celery`
- Requeue failed tasks if needed

---

## 8. SLO Targets

Define Service Level Objectives for accountability:

```yaml
SLO:
  availability: 99.9%       # Uptime target
  error_rate: 0.5%          # Maximum acceptable errors
  latency_p95: 500ms        # 95th percentile response time
  latency_p99: 1000ms       # 99th percentile response time
  database_reachability: 99.99%
  data_consistency: 100%
  
ERROR_BUDGET:
  monthly_allowed_downtime: 43.2 minutes  # 99.9% × 30 days
  monthly_allowed_errors: 4,320 errors    # 0.5% × 1M requests
```

Track SLO compliance in Grafana:

```promql
# Availability SLO
(count(up{job="rpex-backend"} == 1) / count(up{job="rpex-backend"})) * 100

# Error rate SLO
(1 - (sum(rate(http_requests_total{status="5.."}[1h])) / sum(rate(http_requests_total[1h])))) * 100
```

---

## 9. Production Checklist

- [ ] All exporters running and "UP" in Prometheus
- [ ] Alert rules loaded (check /alerts in Prometheus UI)
- [ ] Slack webhooks configured and tested
- [ ] PagerDuty service configured
- [ ] Email notifications working
- [ ] Grafana dashboards imported and pinned
- [ ] SLO dashboards created
- [ ] On-call escalation policy in place
- [ ] Runbooks documented and accessible
- [ ] Team trained on alert response
- [ ] Monthly alert drill scheduled
- [ ] Backup of Grafana dashboards (export JSON)

---

## 10. Troubleshooting

### Metrics not appearing

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check exporter directly
curl http://localhost:9187/metrics  # postgres_exporter

# Check Prometheus scrape logs
docker logs rpex_prometheus | grep -i "scrape\|error"
```

### Alerts not firing

```bash
# Check alert evaluation
curl 'http://localhost:9090/api/v1/query?query=ALERTS'

# Check alert rules
curl 'http://localhost:9090/api/v1/rules'

# Reload Prometheus config (if changed)
docker kill -s HUP rpex_prometheus
```

### Notifications not received

```bash
# Check Alertmanager logs
docker logs rpex_alertmanager | grep -i "slack\|email\|pagerduty"

# Verify webhook URL
curl -X POST <SLACK_WEBHOOK_URL> -d '{"text":"Test"}'

# Check alert routing
curl 'http://localhost:9093/api/v1/routes'
```

---

## 11. Scaling Monitoring

For high-volume metrics (>1M series):

1. **Use remote storage** (S3, Thanos):
   ```yaml
   remote_write:
     - url: http://thanos-receiver:19291/api/v1/receive
   ```

2. **Separate scrape configs by cluster**:
   - Dedicated Prometheus per Kubernetes cluster
   - Thanos for global query

3. **Reduce cardinality**:
   - Drop unnecessary labels
   - Use relabeling to limit series count

4. **Optimize retention**:
   - High-resolution: 7 days
   - Standard: 30 days
   - Archive: Long-term in S3

---

## Support & Escalation

- **Monitoring issues**: Check `/prometheus/targets`
- **Alert storm**: Check `/alertmanager/status` for duplicate alerts
- **Disk full**: Prometheus data exceeds retention → reduce retention or increase storage
- **Notification failures**: Test webhook, check credentials

**Contacts:**
- Platform team (Prometheus/Grafana): [platform-team@company.com]
- On-call engineer (Alert response): [page oncall@company.com]
