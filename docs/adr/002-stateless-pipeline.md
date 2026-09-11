# ADR 002: Stateless Pipeline Architecture in v1 (No Database)

## Status
**Accepted**

## Context
When developers submit code to an automated debugging companion, security and privacy are paramount. Development teams and enterprise engineers frequently handle proprietary source code, internal business logic, and sensitive credentials accidentally pasted into code snippets. 

Introducing a persistent storage layer (e.g., PostgreSQL, MongoDB, or Redis) in version 1 introduces major challenges:
1. **Data Security & Compliance Liability**: Storing user code at rest triggers compliance overhead (SOC2, GDPR, HIPAA) and risks data leaks of proprietary source code.
2. **Operational Complexity**: Managing database connections, migrations, connection pools, schema evolution, and backups increases infrastructure overhead and complicates one-command local runs.
3. **Session Lifecycle**: Code analysis is fundamentally a request-response transaction. Developers submit code, inspect the diffs, copy the test suite, and integrate it into their local IDE. Persistent storage offers minimal value for initial single-session troubleshooting.

## Decision
We declare DevMind v1 as a **strictly stateless, zero-retention architecture**:

1. **No Backend Database**:
   - The FastAPI backend will not connect to any relational, document, or key-value database.
   - Code payloads exist solely in volatile memory for the duration of the request.
   - Once the SSE stream terminates (`event: done` or connection close), all snippet data and intermediate pipeline results are garbage-collected by the Python runtime.

2. **In-Flight Event Streaming**:
   - Intermediate stage results (classification, summary, fix, tests, documentation) are yielded in real-time across the active HTTP connection as Server-Sent Events (`text/event-stream`).
   - The backend does not maintain an in-memory session registry or caching layer across distinct connections.

3. **Client-Side Session State**:
   - The React frontend manages the immediate UI state within React component memory.
   - Optional local history or draft persistence is deferred strictly to client-side `localStorage`, giving the user full autonomy over data clearance.

## Consequences

### Positive
- **Maximum Privacy & Security**: Zero retention ensures proprietary code is never persisted to disk, eliminating data breach vectors for stored code.
- **Zero Infrastructure Friction**: DevMind can be launched immediately via `uvicorn main:app --reload` without running database containers, running migrations, or configuring connection strings.
- **Horizontal Scalability**: Being completely stateless, the backend service can be horizontally autoscaled behind any standard load balancer (e.g., NGINX, AWS ALB) with zero sticky-session or shared-state synchronization requirements.

### Negative
- **No Cross-Device History**: Developers cannot access previous analysis runs from another machine or browser unless they manually export the results.
- **No Shared Team Workspaces**: Collaborative review of analysis runs is not natively supported in v1 without external forwarding.
- **Redundant Processing**: Re-analyzing an identical snippet triggers a fresh execution through the 5 stages (mitigated in future iterations via client-side caching or optional opt-in Redis hashing).
