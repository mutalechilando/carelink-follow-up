CareLink Follow-Up — Architecture and Trade-offs

1. Architecture Summary

CareLink Follow-Up will be delivered as a new module within the existing CareLink ecosystem. The architecture is designed for approximately 1,500 facilities with materially different connectivity, including facilities that may be offline for several days.

I would use an offline-first client with a nationally hosted modular application backend. The backend would initially be a modular monolith rather than a collection of microservices. This gives the team of two senior engineers, five software engineers and two junior developers enough architectural separation without creating unnecessary operational complexity nine months before the first facilities go live.

The core principles are:

- The facility must be able to continue essential follow-up work without a network connection.
- The national platform is the authoritative system of record, but it does not automatically win every conflict. Conflicts are detected using entity versions and resolved according to workflow-specific rules; high-risk clinical conflicts require explicit review rather than silent last-write-wins behaviour.
- Synchronisation must be explicit, observable and idempotent.
- APIs must remain backward-compatible so facilities can be upgraded progressively.
- PHI must be protected in transit, at rest and in operational logs.
- The system must scale through database-efficient queries, pagination and horizontal application scaling rather than loading large patient lists into browsers.
- Deployment and data storage must support an in-country hosting requirement.

 High-level architecture

flowchart TB
    subgraph Facility["Facility / Clinic"]
        UI["CareLink Follow-Up Client<br/>Keyboard-friendly Web/PWA"]
        CACHE["Encrypted Local Store<br/>Assigned patients + reference data"]
        OUTBOX["Offline Outbox<br/>Operations + sync state"]

        UI <--> CACHE
        UI --> OUTBOX
        OUTBOX --> CACHE
    end

    subgraph National["National CareLink Environment"]
        GW["API Gateway / Reverse Proxy"]
        AUTH["Identity & Access Management"]
        APP["CareLink Application<br/>Modular Backend"]
        SYNC["Sync Service / API"]
        DB[("National PostgreSQL<br/>Transactional Data")]
        AUDIT["Audit & Observability"]
        QUEUE["Integration / Job Queue"]
    end

    subgraph External["National / External Systems"]
        LAB["Laboratory Information System"]
        REPORT["National Reporting Platform"]
    end

    UI <-->|HTTPS / API| GW
    OUTBOX <-->|HTTPS / Sync API| GW

    GW --> AUTH
    GW --> APP
    GW --> SYNC

    APP <--> DB
    SYNC <--> DB
    APP --> AUDIT
    SYNC --> AUDIT

    APP <--> QUEUE
    QUEUE <--> LAB
    QUEUE --> REPORT

The browser/client never connects directly to PostgreSQL. All access passes through authenticated APIs. External systems also integrate through defined API or asynchronous integration boundaries rather than accessing CareLink tables directly.



2. Major Components and Communication

 Facility client

The Follow-Up client provides the clinician and facility users with the worklist, patient follow-up details and contact recording functionality.

The client maintains a small encrypted local data store containing the minimum data required to operate while offline. It also maintains an outbox of changes waiting to be synchronised.

The interface is designed for older clinic computers and keyboard-only operation. Large patient lists are paginated and filtered server-side when connected; the client does not attempt to download a 10,000+ patient worklist into the browser.

 API gateway

The gateway/reverse proxy provides a single controlled entry point to CareLink APIs. It handles TLS termination, request limits, routing and basic protection against abusive traffic.

It also provides a useful boundary for future services without requiring the frontend to know where individual backend components are hosted.

 Application backend

The backend is initially a modular monolith with clear modules such as:

- Follow-Up
- Patients
- Visits
- Facilities
- Synchronisation
- Reporting
- Integration
- Audit

The modules have clear ownership boundaries while sharing one transactional database where appropriate.

 National database

PostgreSQL is the primary transactional store for the national system. It maintains authoritative national records, synchronisation state, audit information and reporting data.

Indexes, database-side filtering and pagination are important because the system must support approximately 3,000 concurrent weekday-morning users.

The 3,000 concurrent-user target is not addressed by simply adding application servers. Query patterns are designed first for indexed, bounded result sets, with connection pooling, horizontal application scaling and load testing against realistic morning-peak workloads.

 Integration layer

Laboratory and reporting integrations are separated from the core request/response path.

Where an external system can accept asynchronous messages, CareLink places integration work onto a queue and records delivery status. This prevents a slow laboratory or reporting system from making the clinician's patient screen slow or unavailable.



3. Data Approach: Facility and National

The system uses a two-level data model.

 Data held at the facility

Only data necessary for local clinical operation and offline follow-up is cached locally. This may include:

- patients assigned to the facility;
- relevant appointment and visit information;
- follow-up status;
- required facility/reference data;
- locally generated follow-up contact attempts;
- synchronisation metadata.

The local store should be encrypted and protected by the device's operating-system security mechanisms.

The system should avoid creating a complete national patient database at every facility. This reduces both privacy exposure and the amount of data that must be synchronised.

 Data held nationally

The national platform holds:

- authoritative patient and visit records;
- facility and user information;
- synchronisation state;
- audit history;
- reporting data;
- integration records;
- national reference data.

The national database is the authoritative source when resolving conflicts involving nationally shared clinical records.

 Reconciliation

Every locally generated operation receives a unique operation ID and records:

- device ID;
- authenticated user;
- timestamp;
- entity ID;
- operation type;
- base/server version where applicable.

The client sends pending operations through the synchronisation API.

The server processes operations idempotently. If the same operation is submitted twice because of a retry, it must not create two clinical records.

Synchronisation follows a pattern of:

1. Push locally generated operations.
2. Receive acknowledgements/conflicts.
3. Pull changes made nationally since the client's last successful cursor.
4. Apply changes locally.
5. Update the local sync cursor.
6. Repeat until caught up.

Append-only events such as follow-up contact attempts are straightforward to reconcile. Clinical facts such as appointments and visits require version checking and explicit conflict handling rather than silent last-write-wins behaviour.



4. API Approach and External Integrations

CareLink uses versioned REST APIs for synchronous application operations.

For example:

GET  /api/v1/follow-up
POST /api/v1/follow-up/{id}/contacted
POST /api/v1/sync/push
GET  /api/v1/sync/changes?cursor=...

APIs should provide:

- explicit request/response schemas;
- pagination;
- authentication and authorisation;
- correlation IDs;
- consistent error responses;
- rate limiting;
- backwards-compatible versioning;
- idempotency for operations that may be retried.

 Laboratory integration

The laboratory system should integrate through a defined integration API or message boundary.

For example:

CareLink → Lab Integration → Laboratory System
Laboratory System → Lab Integration → CareLink

Laboratory results should be correlated using stable identifiers rather than names alone.

The integration should tolerate temporary laboratory-system failures. Failed messages are retained for retry, with operational alerts when delivery is delayed.

The clinician should not have to wait synchronously for the laboratory system to respond unless the clinical workflow genuinely requires a synchronous result.

 Reporting integration

Reporting should consume approved, validated CareLink data through a reporting API or asynchronous export mechanism.

The reporting platform should not query the operational database directly.

This protects clinical transactions from reporting workloads and gives the reporting contract a controlled interface that can evolve independently.



5. Authentication and Authorisation

Authentication should use the Ministry's or CareLink ecosystem's central identity provider, preferably OIDC/OAuth 2.0, rather than application-specific passwords.

Access is controlled through role-based access control combined with facility/district scope.

| User group | Typical access |
|||
| Clinician | Patient/follow-up information and follow-up actions within their assigned facility |
| Facility Administrator | Facility users, configuration and operational information for their facility; no unnecessary access to national administration |
| District Officer | Read access across facilities within their district and district-level operational/reporting functions |
| National User | Authorised national-level access, reporting and administration according to assigned privileges |

The system should apply least privilege. A user's role alone is not sufficient; the API also checks the organisational scope associated with the user.

For example, a clinician from Facility A cannot obtain Facility B's patient records simply by changing `facility_id` in a request.

 When a facility is online

The client authenticates against the identity service and receives an access token. APIs validate the token and enforce role and organisational scope.

 When a facility is offline

The client cannot contact the identity provider, so it must not simply accept arbitrary credentials indefinitely.

A previously authenticated device may receive a time-limited offline session credential protected by the device/runtime's secure storage mechanism. The exact mechanism will depend on whether the supported client is a browser/PWA or controlled device runtime.

Offline access should be:

- limited to the facility's previously authorised data;
- limited to approved workflows;
- time-bounded;
- auditable;
- revocable when the device next reconnects.

High-risk administrative actions should require connectivity and fresh authentication.

If a user's account has been disabled while the facility is offline, the client cannot know immediately. Therefore offline sessions should have a defined maximum lifetime and the device should revalidate permissions as soon as connectivity returns.



6. Facilities Offline for Several Days

Offline operation is a first-class capability rather than an error mode.

While offline, the clinician can:

1. Open the locally cached follow-up worklist.
2. Review relevant patient information.
3. Record follow-up contact attempts.
4. Continue other explicitly approved offline workflows.
5. See when the locally cached data was last synchronised.

Each change is written locally and added to the outbox.

The user should see a clear status such as:

> Offline — changes saved on this device. Last synchronised: Monday 08:42.

This is preferable to showing apparently current data when the system may be several days out of date.

When connectivity returns, synchronisation happens automatically with retry/backoff and is also available through a manual Sync now action.

A failed synchronisation must not discard locally saved work.

For a facility that has been offline for several days, the system may have a substantial backlog. Synchronisation therefore needs:

- batching;
- resumable cursors;
- retry with exponential backoff and jitter;
- idempotent operations;
- conflict reporting;
- visible sync progress;
- monitoring of sync age and queue depth.



7. Monitoring: What a Clinic Would Recognise

Technical metrics should be translated into operational indicators that matter to facilities.

| Technical signal | Clinic-recognisable health measure |
|||
| API latency | "Patient worklist opens within an acceptable time." |
| API error rate | "The system is not repeatedly failing when staff save work." |
| Sync queue depth | "My offline changes are being sent successfully." |
| Sync age | "The data shown is no more than X hours/days old." |
| Failed sync operations | "My recorded contacts are not stuck waiting to upload." |
| Database health | "The worklist and patient searches remain responsive." |
| Integration failures | "Laboratory/reporting results are arriving without unexplained delays." |
| Authentication failures | "Staff can sign in and remain authorised to use the system." |
| Disk/storage utilisation | "The system will not unexpectedly stop because storage is full." |

I would establish explicit service objectives before national rollout, for example:

- 99.9% monthly availability for the national service, excluding planned maintenance;
- 95% of online follow-up worklist requests complete within an agreed latency target;
- successful sync for 99% of eligible operations within a defined period after connectivity returns;
- zero unexplained loss of locally recorded operations;
- critical integration failures detected and alerted within minutes.

Monitoring should include correlation IDs, operation IDs and device/facility identifiers, but never log unnecessary patient names, national IDs or other PHI.



8. Deployment and Data Residency

If the Ministry requires data to remain in-country, the production environment should be hosted in an approved in-country government or contracted data centre/cloud environment.

The production topology would include:

Internet / Ministry Network
          |
     Load Balancer
          |
   Application Nodes
      /        \
   API Node   API Node
        \      /
      PostgreSQL HA
          |
   Encrypted Backups

Application nodes should be stateless so that additional capacity can be added as usage grows.

The database should have:

- encryption at rest;
- encrypted backups;
- tested restoration procedures;
- role-based administrative access;
- high availability where infrastructure permits;
- network isolation from public access.

Secrets should be stored in an appropriate secrets-management mechanism rather than source code or configuration committed to Git.

If national infrastructure supports it, I would target an initial recovery objective such as RPO ≤15 minutes and RTO ≤1 hour, subject to Ministry infrastructure and budget constraints. These should be formally agreed before production rather than assumed.



9. Five Largest Technical Risks

 1. Extended connectivity outages

Risk: Facilities may remain offline for days, creating stale data and large synchronisation backlogs.

Mitigation:

- offline-first client;
- encrypted local store;
- durable outbox;
- resumable synchronisation;
- idempotent operations;
- sync-age monitoring;
- explicit conflict handling;
- facility-visible sync status.

 2. Clinical data conflicts or duplicate records

Risk: The same patient or clinical record may be changed at multiple locations or submitted repeatedly after retries.

Mitigation:

- stable identifiers;
- operation IDs and idempotency;
- optimistic version checks;
- server-side validation;
- conflict queues;
- clinical/records review for high-risk duplicate merges;
- complete audit trail.

 3. PHI/security breach

Risk: A national EHR contains highly sensitive information and has a large user/device population.

Mitigation:

- central identity management;
- least privilege;
- facility/district scope checks;
- TLS;
- encryption at rest;
- minimal local data;
- secure device management;
- audit logging;
- secrets management;
- no PHI in application logs;
- regular security testing.

 4. Performance degradation at national scale

Risk: Approximately 3,000 concurrent users and very large follow-up lists could cause slow queries and poor clinic experience.

Mitigation:

- indexed relational queries;
- server-side filtering and pagination;
- avoid N+1 queries;
- connection pooling;
- stateless application scaling;
- performance/load testing using realistic datasets;
- separate reporting workloads from transactional workloads.

 5. Integration or release failure

Risk: Laboratory/reporting dependencies or application releases could disrupt clinical operations.

Mitigation:

- versioned APIs;
- backwards-compatible contracts;
- asynchronous integration where appropriate;
- retry queues;
- contract tests;
- expand/contract database migrations;
- feature flags;
- staged rollout;
- pilot facilities before national rollout;
- rollback procedures.



10. Significant Architecture Trade-offs

 Trade-off 1: Modular monolith vs microservices

Rejected alternative: Starting with microservices.

Microservices would provide stronger independent deployment and scaling boundaries, but they would also introduce service discovery, distributed tracing, deployment complexity, network failure modes and additional operational overhead.

With seven engineers plus two juniors and nine months to first go-live, I would start with a modular monolith with strict module boundaries.

If evidence later shows that a component such as reporting or integration requires independent scaling, it can be extracted behind an existing API boundary.

Decision: Modular monolith first; extract services when there is a demonstrated operational or scaling reason.

 Trade-off 2: Online-only web application vs offline-first client

Rejected alternative: Online-only operation.

An online-only system is simpler to build and operate, but it does not satisfy the reality of approximately 1,100 facilities with intermittent or offline connectivity.

Decision: Offline-first for approved workflows, accepting the additional complexity of synchronisation, conflict resolution and local data security.

This is the most important architectural complexity introduced by the operating environment.

 Trade-off 3: Local copy of all national data vs minimum necessary facility data

Rejected alternative: Replicating the national patient database to every facility.

This would simplify some offline queries but would significantly increase privacy exposure, storage requirements, synchronisation traffic and duplicate/conflict risk.

Decision: Each facility receives only the minimum data required for its authorised workflows.

 Trade-off 4: Synchronous integrations vs asynchronous integration

Rejected alternative: Making every laboratory/reporting operation synchronous.

This provides immediate feedback but couples CareLink availability and response time to external systems.

Decision: Use synchronous APIs where immediate responses are necessary and asynchronous queues for operations that can tolerate delay.

 Trade-off 5: Browser/PWA-only offline capability vs controlled device runtime

Rejected alternative: Assuming every existing clinic browser provides reliable modern offline/PWA functionality.

Old clinic computers and browsers make this assumption risky.

The target architecture therefore treats the offline runtime as a deployment decision, not merely a browser feature. During the first implementation phase I would validate the supported browser/device baseline with representative facilities. If the existing browser estate cannot reliably support the required offline capabilities, the same application should be packaged in a controlled runtime or replaced with an approved lightweight client shell.

Decision: Validate the browser baseline early and avoid making national offline reliability dependent on unverified legacy-browser behaviour.



11. Delivery Approach

The nine-month delivery window should be staged:

1. Months 1–2: architecture validation, identity model, data model, offline prototype and integration contracts.
2. Months 3–5: core Follow-Up workflows, synchronisation, security controls and laboratory/reporting adapters.
3. Months 6–7: performance testing, offline testing and pilot deployment.
4. Months 7-8: go/no-go gate: offline recovery, data integrity, security, performance and rollback criteria must pass before expanding beyond pilot facilities.
5. Month 8: pilot facilities, security testing, operational readiness and remediation.
6. Month 9: controlled rollout, monitoring and support readiness.

The first technical milestone should not be "the UI is complete". It should be a proven end-to-end offline/online workflow: create or update a follow-up action offline, reconnect after several days, synchronise it safely, resolve a simulated conflict, and demonstrate that the resulting national record is correct and auditable.

12. Key Architectural Principle

The most important design decision is to treat connectivity, data integrity and security as part of the clinical workflow rather than infrastructure concerns.

A facility that loses connectivity should experience degraded connectivity, not loss of the ability to work. When it reconnects, its locally recorded work should synchronise safely with exactly-once effect, even if the underlying operation is transmitted more than once, with clear visibility of any conflicts or outstanding actions.