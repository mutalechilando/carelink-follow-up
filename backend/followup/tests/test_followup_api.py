from datetime import date, timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from followup.models import Facility, FollowUpContact, Patient, Visit


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def facilities():
    return {
        "mwansa": Facility.objects.create(
            facility_id="FAC-0101",
            name="Mwansa Urban Clinic",
            district="Mwansa",
        ),
        "kalemba": Facility.objects.create(
            facility_id="FAC-0207",
            name="Kalemba Rural Health Centre",
            district="Kalemba",
        ),
    }


@pytest.fixture
def patient(facilities):
    return Patient.objects.create(
        facility=facilities["mwansa"],
        patient_number="API-001",
        first_name="Test",
        last_name="Patient",
        date_of_birth=date(1990, 1, 1),
        sex=Patient.Sex.FEMALE,
    )


@pytest.mark.django_db
def test_get_follow_up_requires_authentication(api_client):
    response = api_client.get("/api/follow-up")

    assert response.status_code == 401


@pytest.mark.django_db
def test_clinician_cannot_access_another_facility(
    api_client,
    facilities,
):
    api_client.credentials(
        HTTP_AUTHORIZATION="Token clinician-mwansa"
    )

    response = api_client.get(
        "/api/follow-up",
        {"facility_id": "FAC-0207"},
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_district_officer_can_access_multiple_facilities(
    api_client,
    facilities,
):
    today = timezone.localdate()

    patient = Patient.objects.create(
        facility=facilities["kalemba"],
        patient_number="API-002",
        first_name="District",
        last_name="Patient",
        date_of_birth=date(1990, 1, 1),
        sex=Patient.Sex.MALE,
    )

    Visit.objects.create(
        patient=patient,
        visit_date=today - timedelta(days=30),
        next_appointment_date=today - timedelta(days=10),
        visit_type=Visit.VisitType.FOLLOW_UP,
    )

    api_client.credentials(
        HTTP_AUTHORIZATION="Token district-chembe"
    )

    response = api_client.get(
        "/api/follow-up",
        {"facility_id": "FAC-0207"},
    )

    assert response.status_code == 200
    assert response.data["pagination"]["total"] == 1


@pytest.mark.django_db
def test_clinician_can_record_contact(
    api_client,
    patient,
):
    api_client.credentials(
        HTTP_AUTHORIZATION="Token clinician-mwansa"
    )

    response = api_client.post(
        f"/api/follow-up/{patient.id}/contacted",
        {
            "contacted_at": "2026-10-06T10:30:00Z",
            "note": "Patient contacted successfully.",
        },
        format="json",
    )

    assert response.status_code == 204

    contact = FollowUpContact.objects.get(patient=patient)

    assert contact.note == "Patient contacted successfully."
    assert contact.contacted_at is not None


@pytest.mark.django_db
def test_district_officer_cannot_record_contact(
    api_client,
    patient,
):
    api_client.credentials(
        HTTP_AUTHORIZATION="Token district-chembe"
    )

    response = api_client.post(
        f"/api/follow-up/{patient.id}/contacted",
        {
            "contacted_at": "2026-10-06T10:30:00Z",
            "note": "Attempted contact.",
        },
        format="json",
    )

    assert response.status_code == 403
    assert not FollowUpContact.objects.filter(patient=patient).exists()


@pytest.mark.django_db
def test_contact_for_missing_patient_returns_404(api_client):
    api_client.credentials(
        HTTP_AUTHORIZATION="Token clinician-mwansa"
    )

    response = api_client.post(
        "/api/follow-up/999999/contacted",
        {
            "contacted_at": "2026-10-06T10:30:00Z",
            "note": "Attempted contact.",
        },
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_invalid_contact_request_returns_400(
    api_client,
    patient,
):
    api_client.credentials(
        HTTP_AUTHORIZATION="Token clinician-mwansa"
    )

    response = api_client.post(
        f"/api/follow-up/{patient.id}/contacted",
        {
            "contacted_at": "not-a-date",
            "note": "",
        },
        format="json",
    )

    assert response.status_code == 400
    assert response.data["error"]["code"] == "INVALID_REQUEST"