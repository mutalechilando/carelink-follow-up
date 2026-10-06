from datetime import date, timedelta

from django.db.models import Exists, F, OuterRef, Q
from django.utils import timezone

from .models import Visit


def get_follow_up_visits(
    *,
    facility_id=None,
    overdue_days=7,
):
    """
    Return patients whose most recent visit created an appointment that is
    more than `overdue_days` days in the past and who have had no visit
    since that appointment.
    """
    today = timezone.localdate()
    cutoff_date = today - timedelta(days=overdue_days)

    later_visit = Visit.objects.filter(
        patient_id=OuterRef("patient_id"),
        visit_date__gt=OuterRef("visit_date"),
    )

    visits = (
        Visit.objects
        .select_related("patient", "patient__facility")
        .annotate(
            has_later_visit=Exists(later_visit),
        )
        .filter(
            has_later_visit=False,
            next_appointment_date__isnull=False,
            next_appointment_date__lt=cutoff_date,
        )
        .order_by("next_appointment_date", "patient_id")
    )

    if facility_id:
        visits = visits.filter(patient__facility__facility_id=facility_id)

    return visits