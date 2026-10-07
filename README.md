# CareLink Follow-Up — Technical Assessment

## 1. What I Built

This submission implements a working vertical slice of the CareLink patient follow-up workflow.

### Backend

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
- Automated backend tests covering service logic, API behaviour, permissions and query efficiency.

### Frontend

- React + TypeScript + Vite.
- Typed API service layer separating HTTP calls from presentation components.
- Follow-up list with facility/status filters, sorting and pagination.
- Loading, empty, error and retry states.
- Contact workflow using an accessible dialog.
- Status displayed using text as well as visual styling.
- Keyboard-accessible semantic controls and table structure.

## 2. What Is Stubbed / Deliberately Simplified

This is an assessment vertical slice rather than a production national EHR.

- Authentication uses static assessment tokens rather than a production identity provider.
- Production OIDC/OAuth2, Ministry identity integration and full user administration are designed but not implemented.
- The production offline-first client, durable sync queue and conflict-resolution mechanism are designed in `D-resilience.md` but are outside this vertical slice.
- The external laboratory and national reporting integrations are architectural boundaries/stubs rather than live integrations.
- Production deployment, monitoring infrastructure and in-country hosting are described in the architecture but are not provisioned in this repository.

## 3. Stack and Rationale

**Backend:** Python, Django, Django REST Framework and PostgreSQL.

Django/DRF provides a mature API and database framework with strong validation, transactions and security features. PostgreSQL provides reliable relational constraints and indexing appropriate for clinical data.

**Frontend:** React, TypeScript and Vite.

React supports a maintainable component model, while TypeScript reduces errors at the API/UI boundary. Vite keeps the assessment frontend simple and fast to build.

**Testing:** pytest/pytest-django for backend tests and TypeScript/ESLint build checks for frontend quality.

## 4. Running from a Clean Machine

### Prerequisites

- Python 3.14+
- Node.js 24+
- PostgreSQL 17+
- npm

### Backend

From the repository:

```bash
cd backend
python -m venv ../.venv
```

Activate the virtual environment.

Windows PowerShell:

```powershell
..\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

### PostgreSQL

Create a PostgreSQL application user and database. For example, from `psql` as a PostgreSQL administrator:

```sql
CREATE USER carelink_app WITH PASSWORD 'your-local-password';
CREATE DATABASE carelink OWNER carelink_app;
```

Configure the Django environment variables in PowerShell:

```powershell
$env:POSTGRES_DB="carelink"
$env:POSTGRES_USER="carelink_app"
$env:POSTGRES_PASSWORD="<your-local-password>"
$env:POSTGRES_HOST="localhost"
$env:POSTGRES_PORT="5432"
$env:DJANGO_SECRET_KEY="<your-local-development-secret>"
```

The password and secret above are local development values only. Do not commit them to the repository.

Run migrations:

```powershell
python manage.py migrate
```

Load the assessment data:

```powershell
python manage.py seed_data
```

Run the backend:

```powershell
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

### Backend tests

Run:

```powershell
pytest -q
```

The expected result for the submitted implementation is:

```text
13 passed
```

## 5. Demo Authentication

The assessment implementation uses static tokens to represent authenticated users.

| Token | Role | Facility scope |
|---|---|---|
| `clinician-mwansa` | Clinician | `FAC-0101` |
| `clinician-kalemba` | Clinician | `FAC-0207` |
| `district-chembe` | District Officer | All facilities |

These are assessment-only credentials and are not intended for production use.

The production design replaces these static tokens with OIDC/OAuth2 and centrally managed identity and access controls.

## 6. Frontend

In a second terminal:

```powershell
cd frontend
npm install
```

Create a local frontend environment file from the supplied example:

```powershell
Copy-Item .env.example .env.local
```

Set the following values in `.env.local`:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_API_TOKEN=clinician-mwansa
```

The token can be changed to one of the assessment users listed above to demonstrate different access scopes.

Start the frontend:

```powershell
npm run dev
```

Open the local development URL shown by Vite, normally:

```text
http://localhost:5173
```

For a production-like frontend build:

```powershell
npm run lint
npm run build
```

## 7. Follow-Up Rule and Assumptions

The assessment rule was interpreted as:

> A patient is due for follow-up when their most recent applicable visit has a `next_appointment_date` more than `overdue_days` in the past and there has been no visit after that appointment date.

The distinction is intentional.

For example, if a patient was given a 5 September appointment but attended another visit on 3 September, that visit does not satisfy the 5 September appointment. A visit on 6 September does.

I also assumed:

- `overdue_days=7` is the default threshold;
- dates are evaluated using the service's configured date/time;
- pagination is required at API level rather than loading 10,000+ patients into the browser;
- patient follow-up records are facility-scoped for clinicians.

### Additional schema elements

The implementation adds a `Facility` model to support facility-scoped access and filtering, and a `FollowUpContact` model to record contact activity without modifying the underlying visit history.

Additional database indexes and constraints support facility filtering, follow-up queries and data integrity.

## 8. API Contract

### Follow-up list

```text
GET /api/follow-up
```

Supported query parameters:

- `facility_id`
- `status`
- `overdue_days`
- `sort`
- `page`
- `page_size`

Example:

```text
GET /api/follow-up?facility_id=FAC-0101&status=overdue&sort=days_overdue_desc&page=1&page_size=50
```

### Record contact

```text
POST /api/follow-up/{id}/contacted
```

Example body:

```json
{
  "contacted_at": "2026-10-06T09:14:00Z",
  "note": "Patient contacted successfully."
}
```

A successful request returns HTTP `204`.

### Error format

Errors use a consistent structure:

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "facility_id is required",
    "correlation_id": "8c21-44f1"
  }
}
```

## 9. What I Left Out and What I Would Do Next

The main production capability left out is the full offline-first synchronization implementation. This was deliberately separated from the assessment's follow-up vertical slice because it requires additional client, server and conflict-resolution infrastructure.

Next steps would be:

1. Implement the durable offline outbox and idempotent synchronization described in `D-resilience.md`.
2. Replace static tokens with Ministry-approved identity and access management.
3. Complete automated frontend/API integration and accessibility testing.
4. Implement laboratory and national reporting integrations.
5. Add production observability, security controls and deployment automation.
6. Conduct performance and offline synchronization testing at representative national scale.

## 10. Accessibility Decisions

Three specific accessibility decisions were made:

1. **Semantic controls:** filters, buttons and actions use native HTML controls rather than clickable `div` elements, supporting keyboard and assistive technology use.
2. **Accessible status communication:** follow-up status is represented with text and labels rather than relying on colour alone.
3. **Associated labels and announcements:** form controls have explicit labels, the contact dialog has an accessible name, and errors are exposed through an appropriate alert mechanism.

### One thing deliberately not done

I did not implement a complete automated accessibility test suite, such as axe-based browser testing, within the assessment timeframe. The interface was instead built around semantic HTML and explicit accessibility considerations.

## 11. Repository Structure

The main submission components are:

```text
README.md
docs/
      A-architecture.md
      C-review.md
      D-resilience.md
      E-presentation.pdf
      F-practice.md
      G-briefing.md
      declaration.md

backend/
frontend/
```

The backend contains the Django application, migrations, seed command and automated tests. The frontend contains the React/TypeScript application and API service layer.

## 12. Assessment Scope

The repository intentionally distinguishes between:

### Implemented and tested

- Follow-up API
- PostgreSQL data model
- Follow-up calculation
- Filtering, sorting and pagination
- Contact recording
- Facility/role authorisation
- Correlation IDs and error handling
- React/TypeScript follow-up interface
- Backend automated tests
- Frontend lint and production build

### Designed but not implemented

- Production identity provider
- Full offline-first synchronisation
- Durable client outbox
- Idempotency infrastructure
- Conflict-resolution workflow
- Laboratory integration
- National reporting integration
- Production deployment and monitoring