from datetime import timedelta

from django.db.models import Exists, OuterRef, Subquery
from django.utils import timezone

from .models import FollowUpContact, Visit


def get_follow_up_visits(
    *,
    facility_id=None,
    overdue_days=7,
    status="overdue",
):
    """
    Return patients requiring follow-up.

    overdue:
        The most recent visit created an appointment more than N days ago,
        and there has been no visit since that appointment.

    due_soon:
        The most recent visit has a future appointment within N days.

    recently_missed:
        The most recent visit created an appointment that is overdue by
        N days or less.

    The default behaviour remains the assessment's primary overdue rule.
    """
    today = timezone.localdate()
    cutoff_date = today - timedelta(days=overdue_days)
    soon_date = today + timedelta(days=overdue_days)

    later_visit = Visit.objects.filter(
        patient_id=OuterRef("patient_id"),
        visit_date__gt=OuterRef("next_appointment_date"),
    )

    last_contact = FollowUpContact.objects.filter(
        patient_id=OuterRef("patient_id"),
    ).order_by("-contacted_at", "-id")

    visits = (
        Visit.objects
        .select_related("patient", "patient__facility")
        .annotate(
            has_later_visit=Exists(later_visit),
            last_contact_attempt=Subquery(
                last_contact.values("contacted_at")[:1]
            ),
        )
        .filter(
            has_later_visit=False,
            next_appointment_date__isnull=False,
        )
    )

    if status == "overdue":
        visits = visits.filter(
            next_appointment_date__lt=cutoff_date,
        )
    elif status == "recently_missed":
        visits = visits.filter(
            next_appointment_date__gte=cutoff_date,
            next_appointment_date__lt=today,
        )
    elif status == "due_soon":
        visits = visits.filter(
            next_appointment_date__gte=today,
            next_appointment_date__lte=soon_date,
        )

    if facility_id:
        visits = visits.filter(
            patient__facility__facility_id=facility_id,
        )

    return visits