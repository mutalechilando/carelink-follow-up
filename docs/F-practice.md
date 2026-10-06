 CareLink — Delivery and Engineering Practice

 90-Day Improvement Plan

My approach would be to improve delivery reliability without stopping clinical delivery. I would not start with a large rewrite, a new architecture programme or a long delivery freeze. The immediate problem is lack of engineering controls and feedback loops, so I would establish those first and then use evidence to decide where deeper changes are justified.



 Days 1–30 — Stabilise

 What I would change

Team structure

- Establish clear ownership for product areas rather than having work assigned informally.
- Pair the two senior engineers with the wider engineering team for design, review and mentoring.
- Make the QA engineer part of planning and acceptance rather than a final release gate.
- Use the business analyst to maintain acceptance criteria and clarify requirements before development starts.
- Establish a regular engineering/programme refinement session to surface changing requirements early.

Code review

- Require pull requests for production code.
- At least one other engineer reviews every change.
- Security-, database- and clinical-data changes receive senior-engineer review.
- No direct production edits.

The two engineers currently applying fixes directly on production would retain emergency access, but only through an explicit emergency-change process with logging, review and follow-up.

Branching

Adopt a simple short-lived branch model:

```text
main
  |
  +-- feature/...
  |
  +-- fix/...
```

Branches should be small and merged frequently rather than becoming long-running parallel versions.

Testing and CI

- Make existing tests reliable before aggressively increasing coverage.
- Remove or quarantine genuinely flaky tests while investigating their causes.
- Add CI checks for build, unit tests, linting and basic security/static checks.
- Establish a baseline for current coverage and test duration.

Release management

Introduce a lightweight release checklist covering:

- tests passed;
- database migrations reviewed;
- API compatibility checked;
- rollback plan available;
- monitoring confirmed;
- business/clinical acceptance completed.

 What I would deliberately leave alone

I would not:

- rewrite the application;
- introduce microservices;
- replace the whole test framework;
- attempt to clear all 300 backlog items;
- demand 80–90% coverage immediately;
- change the team structure dramatically;
- introduce a complicated branching model.

 How I would know it worked

By day 30 I would expect:

- zero routine direct production changes;
- reproducible CI results;
- 100% of production changes reviewed;
- a measured baseline for deployment time, defects and test reliability;
- fewer emergency fixes;
- an agreed release checklist being used consistently.



 Days 31–60 — Improve Flow

 What I would change

Testing

Prioritise meaningful automated tests around the highest-risk clinical workflows rather than chasing a coverage percentage.

Start with:

- patient creation/update;
- follow-up eligibility;
- clinical writes;
- permissions;
- synchronisation;
- reporting/integration boundaries.

CI/CD

Move from "CI checks" towards a repeatable deployment pipeline:

```text
Commit
  ↓
Build
  ↓
Tests
  ↓
Security/quality checks
  ↓
Deploy to test/staging
  ↓
Acceptance
  ↓
Production
```

Deployments should be repeatable rather than engineers manually copying fixes to production.

Release management

Reduce the three-day release process by standardising:

- release candidate process;
- automated deployment;
- database migration checks;
- smoke tests;
- rollback;
- release notes.

Use feature flags where they allow incomplete functionality to be deployed safely without exposing it to users.

Documentation

Assign ownership for API documentation.

API documentation should be updated as part of the definition of done, not treated as a separate documentation project.

Backlog

Triage the 300 items into categories such as:

- critical defects;
- clinical/business priority;
- regulatory/security;
- technical debt;
- improvements;
- obsolete/duplicate items.

Work with programme teams to identify the highest-value items rather than processing the backlog strictly by age.

Technical debt

Create a visible technical-debt register containing:

- problem;
- affected area;
- risk;
- estimated impact;
- proposed remediation;
- owner.

Reserve a predictable portion of engineering capacity for the highest-value debt rather than attempting a wholesale cleanup.

 What I would deliberately leave alone

I would not:

- impose a large process framework;
- introduce story-point targets as a productivity measure;
- require every old component to be rewritten;
- migrate to a new programming language/framework;
- make test coverage the team's primary performance target.

 How I would know it worked

I would look for:

- shorter PR review time;
- fewer failed builds;
- improved meaningful test coverage;
- fewer production defects;
- shorter release duration;
- fewer hotfixes;
- current API documentation for actively used endpoints;
- a backlog with clear priority and ownership.



 Days 61–90 — Optimise and Institutionalise

 What I would change

Introduce a small set of engineering delivery metrics:

- deployment frequency;
- lead time from approved change to production;
- change failure rate;
- mean time to recovery;
- production defects attributable to recent changes;
- hotfix frequency;
- automated test reliability;
- release duration.

I would review these metrics with both engineering and programme teams.

The purpose is not to rank individuals. It is to identify where the delivery system is slowing us down.

 Mentoring

Create regular technical pairing and knowledge-sharing sessions.

Senior engineers should actively mentor the five engineers and two juniors through:

- design reviews;
- pairing on difficult changes;
- code-review feedback;
- incident reviews;
- testing practices.

I would also make sure that critical systems do not have only one person who knows how they work.

 Programme/engineering relationship

Establish a lightweight planning agreement:

- programme teams provide the desired outcome and priority;
- engineering identifies technical constraints, dependencies and risk;
- changes to requirements are made visible rather than silently inserted into active work;
- engineering provides realistic delivery estimates based on evidence;
- both groups review missed assumptions rather than assigning blame.

 What I would deliberately leave alone

I would not optimise areas that have not yet demonstrated a problem.

In particular, I would avoid:

- reorganising the entire department;
- introducing a large DevOps platform programme;
- adopting numerous new tools;
- measuring individual developer productivity;
- forcing a target deployment frequency simply because it is a common industry metric.

 How I would know it worked

At day 90 I would expect measurable improvement in:

- production defect rate;
- change failure rate;
- hotfix frequency;
- release duration;
- PR turnaround;
- CI reliability;
- test coverage of critical workflows;
- backlog clarity;
- API documentation freshness.

The most important outcome would be that clinical services can continue receiving changes through a predictable, reviewable and reversible delivery process.



 The First Two Changes

 1. Stop routine direct production changes

This is the first change because it addresses an immediate and controllable source of risk.

Production changes should go through review, automated checks and a documented deployment path. Emergency access remains available for genuine incidents, but every emergency change must be recorded and reviewed afterwards.

Why first: the current practice can bypass every other control and directly introduce clinical defects.

 2. Establish reliable CI + pull-request review

Every change should have an automated minimum quality gate and peer review before production.

Initially this means:

```text
Pull request
    ↓
Build
    ↓
Reliable tests
    ↓
Lint/quality checks
    ↓
Peer review
    ↓
Staging
    ↓
Production
```

Why second: this creates a repeatable safety net around the development process while also giving the team immediate feedback on code quality and test reliability.

Together, these two changes reduce risk without requiring a delivery freeze.



 How I Would Behave While the Team Is in This State

I would avoid framing the existing problems as individual failures. Direct production changes, weak tests and outdated documentation are symptoms of a delivery system that has allowed unsafe shortcuts to become normal.

As manager, I would set clear expectations around production safety while making the safer path easier than the unsafe one.

I would also protect the team from unrealistic process demands. Programme teams are right that engineering speed matters; engineers are right that constantly changing requirements have a cost. My role would be to make those trade-offs visible, establish priorities and use delivery data to improve the conversation.

The goal after 90 days is not a perfect engineering organisation. It is a team that can change clinical software safely, measure whether it is improving, and continue delivering while doing so.