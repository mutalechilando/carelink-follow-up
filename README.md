 CareLink Follow-Up — Technical Assessment

 1. What I Built

This submission implements a working vertical slice of the CareLink patient follow-up workflow.

 Backend
- Django 5.2 + Django REST Framework API.
- PostgreSQL database.
- `GET /api/follow-up` with:
  - facility filtering;
  - follow-up status filtering;
  - configurable overdue threshold;
  - server-side sorting;
  - server-side pagination.
- `POST /api/follow-up/{id}/contacted` for recording a contact attempt.
- Role-aware access:
  - clinicians can read/write within their facility;
  - district officers can read across facilities but cannot record contacts.
- Consistent API error responses with correlation IDs.
- Database-level querying designed to avoid an N+1 query pattern.
- Seed data matching the assessment scenario.
- Automated backend tests covering service logic, API behavior, permissions and query efficiency.

 Frontend
- React + TypeScript + Vite.
- Typed API service layer separating HTTP calls from presentation components.
- Follow-up list with facility/status filters, sorting and pagination.
- Loading, empty, error and retry states.
- Contact workflow using an accessible dialog.
- Status displayed using text as well as visual styling.
- Keyboard-accessible semantic controls and table structure.

 2. What Is Stubbed / Deliberately Simplified

This is an assessment vertical slice rather than a production national EHR.

- Authentication uses static assessment tokens rather than a production identity provider.
- Production OIDC/OAuth2, Ministry identity integration and full user administration are designed but not implemented.
- The production offline-first client, durable sync queue and conflict-resolution mechanism are designed in `D-resilience.md` but are outside this vertical slice.
- The external laboratory and national reporting integrations are architectural boundaries/stubs rather than live integrations.
- Production deployment, monitoring infrastructure and in-country hosting are described in the architecture but are not provisioned in this repository.

 3. Stack and Rationale

Backend: Python, Django, Django REST Framework and PostgreSQL. Django/DRF provides a mature API and database framework with strong validation, transactions and security features. PostgreSQL provides reliable relational constraints and indexing appropriate for clinical data.

Frontend: React, TypeScript and Vite. React supports a maintainable component model, while TypeScript reduces errors at the API/UI boundary. Vite keeps the assessment frontend simple and fast to build.

Testing: pytest/pytest-django for backend tests and the project's TypeScript/ESLint build checks for frontend quality.

 4. Running from a Clean Machine

 Prerequisites

- Python 3.14+
- Node.js 24+
- PostgreSQL 17+
- npm

 Backend

From the repository:

```bash
cd backend

python -m venv ../.venv
```

Activate the virtual environment.

Windows PowerShell:

```powershell
..\ .venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a PostgreSQL database and application user, then configure the Django database environment variables as documented in the project configuration.

Run migrations:

```bash
python manage.py migrate
```

Load the assessment data:

```bash
python manage.py seed_data
```

Run the backend:

```bash
python manage.py runserver
```

Run tests:

```bash
pytest -q
```

The expected test suite result for the submitted implementation is 13 passing tests.

 Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend expects the backend API base URL and assessment API token through the frontend environment configuration. An `.env.example` file documents the required variables.

For a production-like frontend build:

```bash
npm run lint
npm run build
```

 5. Follow-Up Rule and Assumptions

The assessment rule was interpreted as:

> A patient is due for follow-up when their most recent applicable visit has a `next_appointment_date` more than `overdue_days` in the past and there has been no visit after that appointment date.

The distinction is intentional.

For example, if a patient was given a 5 September appointment but attended another visit on 3 September, that visit does not satisfy the 5 September appointment. A visit on 6 September does.

I also assumed:
- `overdue_days=7` is the default threshold;
- dates are evaluated using the service's configured date/time;
- pagination is required at API level rather than loading 10,000+ patients into the browser;
- patient follow-up records are facility-scoped for clinicians.

 6. What I Left Out and What I Would Do Next

The main production capability left out is the full offline-first synchronization implementation. This was deliberately separated from the assessment's follow-up vertical slice because it requires additional client, server and conflict-resolution infrastructure.

Next steps would be:

1. Implement the durable offline outbox and idempotent synchronization described in `D-resilience.md`.
2. Replace static tokens with Ministry-approved identity and access management.
3. Complete automated frontend/API integration and accessibility testing.
4. Implement laboratory and national reporting integrations.
5. Add production observability, security controls and deployment automation.
6. Conduct performance and offline synchronization testing at representative national scale.

 7. Accessibility Decisions

Three specific accessibility decisions were made:

1. Semantic controls: filters, buttons and actions use native HTML controls rather than clickable `div` elements, supporting keyboard and assistive technology use.
2. Accessible status communication: follow-up status is represented with text and labels rather than relying on colour alone.
3. Associated labels and announcements: form controls have explicit labels, the contact dialog has an accessible name, and errors are exposed through an appropriate alert mechanism.

 One thing deliberately not done

I did not implement a complete automated accessibility test suite (for example, axe-based browser testing) within the assessment timeframe. The interface was instead built around semantic HTML and explicit accessibility