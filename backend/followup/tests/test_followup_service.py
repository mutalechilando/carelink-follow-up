from datetime import date, timedelta

import pytest
from django.utils import timezone

from followup.models import Facility, Patient, Visit
from followup.services import get_follow_up_visits


@pytest.mark.django_db
def test_exactly_seven_days_overdue_is_not_overdue():
    today = timezone.localdate()

    facility = Facility.objects.create(
        facility_id="FAC-TEST-01",
        name="Test Clinic",
        district="Test",
    )

    patient = Patient.objects.create(
        facility=facility,
        patient_number="TEST-001",
        first_name="Boundary",
        last_name="Seven",
        date_of_birth=date(1990, 1, 1),
        sex=Patient.Sex.FEMALE,
    )

    Visit.objects.create(
        patient=patient,
        visit_date=today - timedelta(days=30),
        next_appointment_date=today - timedelta(days=7),
        visit_type=Visit.VisitType.FOLLOW_UP,
    )

    results = get_follow_up_visits(
        overdue_days=7,
        status="overdue",
    )

    assert not results.filter(patient=patient).exists()


@pytest.mark.django_db
def test_eight_days_overdue_is_overdue():
    today = timezone.localdate()

    facility = Facility.objects.create(
        facility_id="FAC-TEST-02",
        name="Test Clinic",
        district="Test",
    )

    patient = Patient.objects.create(
        facility=facility,
        patient_number="TEST-002",
        first_name="Boundary",
        last_name="Eight",
        date_of_birth=date(1990, 1, 1),
        sex=Patient.Sex.MALE,
    )

    Visit.objects.create(
        patient=patient,
        visit_date=today - timedelta(days=30),
        next_appointment_date=today - timedelta(days=8),
        visit_type=Visit.VisitType.FOLLOW_UP,
    )

    results = get_follow_up_visits(
        overdue_days=7,
        status="overdue",
    )

    assert results.filter(patient=patient).exists()

@pytest.mark.django_db
def test_later_visit_removes_patient_from_follow_up():
    today = timezone.localdate()

    facility = Facility.objects.create(
        facility_id="FAC-TEST-03",
        name="Test Clinic",
        district="Test",
    )

    patient = Patient.objects.create(
        facility=facility,
        patient_number="TEST-003",
        first_name="Later",
        last_name="Visit",
        date_of_birth=date(1990, 1, 1),
        sex=Patient.Sex.FEMALE,
    )

    Visit.objects.create(
        patient=patient,
        visit_date=today - timedelta(days=30),
        next_appointment_date=today - timedelta(days=10),
        visit_type=Visit.VisitType.FOLLOW_UP,
    )

    Visit.objects.create(
        patient=patient,
        visit_date=today - timedelta(days=2),
        next_appointment_date=None,
        visit_type=Visit.VisitType.UNSCHEDULED,
    )

    results = get_follow_up_visits(
        overdue_days=7,
        status="overdue",
    )

    assert not results.filter(patient=patient).exists()

@pytest.mark.django_db
def test_visit_before_appointment_does_not_cancel_follow_up():
    today = timezone.localdate()

    facility = Facility.objects.create(
        facility_id="FAC-TEST-04",
        name="Test Clinic",
        district="Test",
    )

    patient = Patient.objects.create(
        facility=facility,
        patient_number="TEST-004",
        first_name="Before",
        last_name="Appointment",
        date_of_birth=date(1990, 1, 1),
        sex=Patient.Sex.FEMALE,
    )

    # Appointment was set for 10 days ago.
    Visit.objects.create(
        patient=patient,
        visit_date=today - timedelta(days=30),
        next_appointment_date=today - timedelta(days=10),
        visit_type=Visit.VisitType.FOLLOW_UP,
    )

    # Patient had another visit BEFORE the appointment date.
    Visit.objects.create(
        patient=patient,
        visit_date=today - timedelta(days=12),
        next_appointment_date=None,
        visit_type=Visit.VisitType.UNSCHEDULED,
    )

    results = get_follow_up_visits(
        overdue_days=7,
        status="overdue",
    )

    assert results.filter(patient=patient).exists()


@pytest.mark.django_db
def test_visit_after_appointment_cancels_follow_up():
    today = timezone.localdate()

    facility = Facility.objects.create(
        facility_id="FAC-TEST-05",
        name="Test Clinic",
        district="Test",
    )

    patient = Patient.objects.create(
        facility=facility,
        patient_number="TEST-005",
        first_name="After",
        last_name="Appointment",
        date_of_birth=date(1990, 1, 1),
        sex=Patient.Sex.MALE,
    )

    # Appointment was set for 10 days ago.
    Visit.objects.create(
        patient=patient,
        visit_date=today - timedelta(days=30),
        next_appointment_date=today - timedelta(days=10),
        visit_type=Visit.VisitType.FOLLOW_UP,
    )

    # Patient returned AFTER the appointment date.
    Visit.objects.create(
        patient=patient,
        visit_date=today - timedelta(days=5),
        next_appointment_date=None,
        visit_type=Visit.VisitType.UNSCHEDULED,
    )

    results = get_follow_up_visits(
        overdue_days=7,
        status="overdue",
    )

    assert not results.filter(patient=patient).exists()