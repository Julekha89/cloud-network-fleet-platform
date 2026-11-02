# Development roadmap

## Phase 1 — Working local MVP (this release)
- [x] Read-only multi-region inventory API
- [x] Simulated health assessment endpoint
- [x] SQLite audit events
- [x] Offline automated tests and CI

## Phase 2 — Safe automation workflows
- [ ] Device change request and plan preview (simulation only)
- [ ] Manual approval gate
- [ ] Deterministic job state machine and idempotent requests
- [ ] Dry-run rollback and failure simulation
- [ ] Tests for invalid transitions, duplicate requests and failed deployments

## Phase 3 — Multi-worker reliability
- [ ] PostgreSQL + Redis design
- [ ] Leases, worker retries, backoff, DLQ, idempotency
- [ ] Regional concurrency limits and worker metrics
- [ ] Container-based integration tests

## Phase 4 — Operability
- [ ] Prometheus metrics, Grafana dashboard and SLOs
- [ ] Structured logs, failure injection and alert tests
- [ ] Secure auth/RBAC, secrets strategy and runbooks
- [ ] Measured capacity and load-test report

All initial phases use simulated infrastructure. No production network actions are authorized.
