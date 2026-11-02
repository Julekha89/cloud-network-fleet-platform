# Cloud Network Fleet Automation & Management Platform

![Phase](https://img.shields.io/badge/Phase-1%20MVP-blue) ![Mode](https://img.shields.io/badge/Network%20Mode-Simulated-green)

An educational **read-only multi-region network fleet management API**, built in Python using the standard library. Designed as a portfolio foundation for network automation, software engineering, and cloud infrastructure roles.

> **Safety and scope:** All devices, identifiers, regions and statuses in this repository are fictional. No production device access, configuration deployment, or cloud resources are involved. The region names are labels, not actual OCI regions. This is not a production-ready platform.

## Features (Phase 1)

- Multi-region router/switch inventory stored in SQLite
- HTTP JSON endpoints for inventory, region filtering, fleet summary, and simulated health checks
- Append-only audit trail for onboarding and assessments
- SQLite parameterized queries and thread-safe storage access
- Read-only API: POST, PUT, DELETE return HTTP 405
- 11 automated unit tests and GitHub Actions CI
- No external Python dependencies; runs on Windows, Linux and macOS

## Architecture

```text
Windows terminal / browser / curl
             |
             v
    ThreadingHTTPServer (localhost:8080)
             |
             v
      FleetStore (SQLite)
        |           |
 Fictional device   Audit trail
 inventory          events
        |
  Simulated health assessments
```

## Run on Windows

Requires **Python 3.10+**. In **PowerShell**, open the extracted project folder:

```powershell
python -m unittest discover -s tests -v
python -m fleet.api
```

Leave the terminal open, then open these URLs in a web browser:

- http://127.0.0.1:8080/healthz
- http://127.0.0.1:8080/api/v1/devices
- http://127.0.0.1:8080/api/v1/devices?region=ap-south-1
- http://127.0.0.1:8080/api/v1/fleet/summary
- http://127.0.0.1:8080/api/v1/devices/blr-edge-01/health
- http://127.0.0.1:8080/api/v1/audit

Stop the service using **Ctrl+C**. It listens on `127.0.0.1` by default, not on the network.

### Optional local SQLite persistence

```powershell
python -m fleet.api --database fleet-local.db
```

> The sample inventory is inserted at startup. Use a fresh database on each startup; persistent sample loading is intentionally basic in Phase 1.

## Sample endpoint response

`GET /api/v1/fleet/summary`

```json
{
  "total": 5,
  "by_status": {"degraded": 1, "healthy": 3, "offline": 1},
  "by_region": {"ap-south-1": 2, "ap-southeast-1": 2, "eu-central-1": 1},
  "source": "simulated"
}
```

## Repository structure

```text
fleet/core.py              SQLite inventory and audit logic
fleet/api.py               Read-only HTTP JSON API
examples/devices.json      Fictional inventory data
tests/test_core.py          11 offline unit tests
.github/workflows/ci.yml   Automated test workflow
docs/ROADMAP.md            Planned phases
.gitignore                 Excludes local secrets and database files
```

## Roadmap

- **Phase 2:** Queue-backed job lifecycle simulator: submitted, approved, running, succeeded, failed; idempotency keys and dry-run change plans.
- **Phase 3:** PostgreSQL + Redis worker orchestration, retries with backoff, concurrency controls, and failure injection.
- **Phase 4:** Containerization, metrics, a dashboard, SLOs, structured logging, integration tests, and operations runbooks.
- **Later:** Authorized real-device adapters, authentication/RBAC, secret management and production-hardening review.

## Limitations

No authentication; access is limited to local loopback by default. Status values are predefined fixture data, not measured metrics. There is no distributed coordination, deployment, rollback, Kubernetes or real cloud provisioning yet. Unit tests do not constitute production validation. No commercial or company-sensitive data is included.

## Career relevance

Demonstrates Python application design, network inventory modeling, HTTP APIs, SQLite persistence, testing, observability foundations, and safe staged automation. A stepping stone toward OCI-style fleet engineering; **not** an Oracle or OCI product.
