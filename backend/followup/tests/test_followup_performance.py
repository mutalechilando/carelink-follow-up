import pytest
from datetime import date, timedelta

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from followup.models import Facility, Patient, Visit
from followup.services import get_follow_up_visits


@pytest.mark.django_db
def test_follow_up_query_does_not_create_n_plus_one_queries():
    today = timezone.localdate()

    facility = Facility.objects.create(
        facility_id="FAC-PERF",
        name="Performance Clinic",
        district="Performance",
    )

    for index in range(50):
        patient = Patient.objects.create(
            facility=facility,
            patient_number=f"PERF-{index:04d}",
            first_name=f"Patient{index}",
            last_name="Performance",
            date_of_birth=date(1990, 1, 1),
            sex=Patient.Sex.FEMALE,
        )

        Visit.objects.create(
            patient=patient,
            visit_date=today - timedelta(days=30),
            next_appointment_date=today - timedelta(days=10),
            visit_type=Visit.VisitType.FOLLOW_UP,
        )

    with CaptureQueriesContext(connection) as queries:
        results = list(
            get_follow_up_visits(
                facility_id="FAC-PERF",
                overdue_days=7,
                status="overdue",
            )
        )

    assert len(results) == 50

    # The important property is that query count remains effectively
    # constant as patient count grows.
    assert len(queries) <= 5