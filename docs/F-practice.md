# CareLink — Delivery and Engineering Practice

## 90-Day Improvement Plan

My approach would be to improve delivery reliability without stopping clinical delivery. I would not start with a large rewrite, new architecture programme or long delivery freeze. The immediate problem is a lack of engineering controls and reliable feedback loops, so I would establish those first and then use evidence to decide where deeper changes are justified.

## Days 1–30 — Stabilise

### What I would change

#### Team structure

- Establish clear ownership for product areas rather than assigning work informally.
- Pair the two senior engineers with the wider team for design, review and mentoring.
- Involve QA in planning and acceptance, not only at the end of development.
- Use the BA to establish clear acceptance criteria before development starts.
- Establish regular engineering/programme refinement to surface changing requirements early.

#### Code review and branching

- Establish a lightweight agreed coding standard covering naming, formatting, error handling, logging, security-sensitive code and testing expectations, enforced through automated formatting/linting where practical.
- Require a pull request and peer review for all production changes.
- Security, database and clinical-data changes receive senior-engineer review.
- Stop routine direct production changes. Emergency access remains available, but every emergency change must be logged, reviewed and followed up.
- Use simple short-lived `feature/*` and `fix/*` branches merged frequently into `main`.

#### Testing and CI

- Stabilise existing tests before aggressively increasing coverage.
- Investigate or quarantine genuinely flaky tests.
- Establish CI for build, tests, linting and basic security/static checks.
- Baseline coverage, test reliability and execution time.

#### Release management

Introduce a lightweight release checklist covering tests, migrations, API compatibility, rollback, monitoring and clinical/business acceptance.

### What I would deliberately leave alone

- No rewrite, microservices programme or new framework.
- No attempt to clear all 300 backlog items.
- No immediate 80–90% coverage target.
- No complicated branching model or major organisational restructure.

### How I would know it worked

By day 30:

- No unapproved routine direct production changes.
- Production changes are reviewed.
- CI results are reproducible.
- Baseline metrics are available.
- Emergency fixes are fewer and traceable.
- The release checklist is being used consistently.

## Days 31–60 — Improve Flow

### What I would change

Prioritise automated tests around the highest-risk clinical workflows: patient records, follow-up eligibility, clinical writes, permissions, synchronisation and integration boundaries.

Move from basic CI checks to a repeatable delivery pipeline:

```text
Commit → Build → Test → Security/quality checks → Staging → Acceptance → Production
```

Standardise release candidates, migration checks, smoke tests, rollback and release notes. Use feature flags where they reduce release risk.

Make API documentation part of the definition of done and assign ownership for keeping actively used endpoints current.

Triage the 300-item backlog into defects, clinical/business priority, regulatory/security, technical debt, improvements and obsolete/duplicate items. Establish clear priority and ownership rather than processing items simply by age.

Create a visible technical-debt register with risk, impact, owner and proposed remediation, and reserve predictable capacity for the highest-value debt.

### What I would deliberately leave alone

I would not introduce a heavy process framework, make story points or test coverage individual performance measures, rewrite legacy components without evidence, or migrate technologies simply for their own sake.

### How I would know it worked

I would expect fewer failed builds and production defects, fewer hotfixes, shorter release duration, improved meaningful test coverage, current documentation for active APIs, and a backlog with clear priority and ownership.

## Days 61–90 — Optimise and Institutionalise

### What I would change

Introduce a small set of delivery metrics:

- Deployment frequency.
- Lead time from approved change to production.
- Change failure rate.
- Mean time to recovery.
- Production defects attributable to recent changes.
- Hotfix frequency.
- Test reliability.
- Release duration.

I would review these with both engineering and programme teams. The purpose is to improve the delivery system, not rank individuals.

Formalise mentoring through design reviews, pairing, code-review feedback and incident reviews. Senior engineers should actively mentor the five engineers and two juniors, while reducing single-person dependency on critical systems.

Establish a lightweight engineering/programme planning agreement: programme teams define outcomes and priorities; engineering identifies constraints, dependencies and risk; requirement changes are made visible; estimates are evidence-based; and missed assumptions are reviewed without blame.

### What I would deliberately leave alone

I would avoid department-wide reorganisation, a large DevOps platform programme, unnecessary tooling, individual developer productivity metrics and arbitrary deployment-frequency targets.

### How I would know it worked

By day 90 I would expect measurable improvement in production defects, change failure rate, hotfix frequency, release duration, PR turnaround, CI reliability, critical-workflow test coverage, backlog clarity and documentation freshness.

The key outcome is that clinical services can continue receiving changes through a predictable, reviewable and reversible delivery process.

## The First Two Changes

### 1. Stop routine direct production changes

This is the first change because it is an immediate and controllable source of risk. Production changes should go through review, automated checks and a documented deployment path. Emergency access remains available for genuine incidents, but every emergency change must be recorded and reviewed afterwards.

**Why first:** it removes a shortcut that can bypass every other engineering control and directly introduce clinical defects.

### 2. Establish reliable CI and pull-request review

Every change should have an automated minimum quality gate and peer review before production:

```text
Pull request → Build → Reliable tests → Quality/security checks → Staging → Production
```

**Why second:** this creates a repeatable safety net around development while exposing test and quality problems early.

Together, these two changes reduce risk immediately without requiring a delivery freeze.

## How I Would Behave While the Team Is in This State

I would push for these minimum engineering standards to become team agreements rather than personal preferences: reviewed production changes, reliable CI, documented release procedures, clear acceptance criteria and evidence-based prioritisation.

I would avoid treating the current problems as individual failures. Direct production changes, weak tests and outdated documentation are symptoms of a delivery system that has allowed unsafe shortcuts to become normal.

I would set clear expectations around production safety while making the safe path easier than the unsafe one. I would also protect the team from unrealistic process demands: programme teams are right that engineering speed matters, while engineers are right that constantly changing requirements have a cost. My role would be to make those trade-offs visible, establish priorities and use delivery evidence to improve the conversation.

The goal after 90 days is not a perfect engineering organisation. It is a team that can change clinical software safely, measure whether it is improving, and continue delivering while doing so.