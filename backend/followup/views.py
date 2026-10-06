import logging

from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .middleware import api_error
from .models import FollowUpContact, Patient
from .serializers import FollowUpContactSerializer, FollowUpSerializer
from .services import get_follow_up_visits


logger = logging.getLogger(__name__)


ALLOWED_STATUSES = {
    "overdue",
    "due_soon",
    "recently_missed",
}

ALLOWED_SORTS = {
    "days_overdue": "-next_appointment_date",
    "-days_overdue": "next_appointment_date",
}


class FollowUpListView(APIView):
    def get(self, request):
        correlation_id = request.correlation_id
        user = request.user

        try:
            overdue_days = int(
                request.query_params.get("overdue_days", 7)
            )
        except ValueError:
            return api_error(
                code="INVALID_PARAMETER",
                message="overdue_days must be an integer.",
                correlation_id=correlation_id,
                status=400,
            )

        if overdue_days < 0:
            return api_error(
                code="INVALID_PARAMETER",
                message="overdue_days must be zero or greater.",
                correlation_id=correlation_id,
                status=400,
            )

        status = request.query_params.get("status", "overdue")

        if status not in ALLOWED_STATUSES:
            return api_error(
                code="INVALID_PARAMETER",
                message=(
                    "status must be one of: overdue, due_soon, "
                    "recently_missed."
                ),
                correlation_id=correlation_id,
                status=400,
            )

        sort = request.query_params.get("sort", "days_overdue")

        if sort not in ALLOWED_SORTS:
            return api_error(
                code="INVALID_PARAMETER",
                message=(
                    "sort must be one of: days_overdue, -days_overdue."
                ),
                correlation_id=correlation_id,
                status=400,
            )

        try:
            page = int(request.query_params.get("page", 1))
            page_size = int(request.query_params.get("page_size", 25))
        except ValueError:
            return api_error(
                code="INVALID_PARAMETER",
                message="page and page_size must be integers.",
                correlation_id=correlation_id,
                status=400,
            )

        if page < 1:
            return api_error(
                code="INVALID_PARAMETER",
                message="page must be greater than zero.",
                correlation_id=correlation_id,
                status=400,
            )

        if page_size < 1 or page_size > 100:
            return api_error(
                code="INVALID_PARAMETER",
                message="page_size must be between 1 and 100.",
                correlation_id=correlation_id,
                status=400,
            )

        facility_id = request.query_params.get("facility_id")

        if user.role == "CLINICIAN":
            if facility_id and facility_id != user.facility_id:
                return api_error(
                    code="FORBIDDEN",
                    message="Clinicians can only access their own facility.",
                    correlation_id=correlation_id,
                    status=403,
                )

            facility_id = user.facility_id

        elif user.role == "DISTRICT_OFFICER":
            pass

        else:
            return api_error(
                code="FORBIDDEN",
                message="This role cannot access follow-up data.",
                correlation_id=correlation_id,
                status=403,
            )

        visits = get_follow_up_visits(
            facility_id=facility_id,
            overdue_days=overdue_days,
            status=status,
        ).order_by(ALLOWED_SORTS[sort], "patient_id")

        total = visits.count()

        offset = (page - 1) * page_size
        paginated_visits = visits[offset:offset + page_size]

        serializer = FollowUpSerializer(
            paginated_visits,
            many=True,
        )

        logger.info(
            "Follow-up list requested",
            extra={
                "correlation_id": correlation_id,
                "role": user.role,
                "facility_id": facility_id,
                "status": status,
                "page": page,
                "page_size": page_size,
                "result_count": len(serializer.data),
                "total_count": total,
            },
        )

        return Response(
            {
                "results": serializer.data,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": (
                        (total + page_size - 1) // page_size
                    ),
                },
            }
        )

class FollowUpContactView(APIView):
    def post(self, request, pk):
        correlation_id = request.correlation_id
        user = request.user

        try:
            patient = Patient.objects.select_related("facility").get(pk=pk)
        except Patient.DoesNotExist:
            return api_error(
                code="NOT_FOUND",
                message="Patient was not found.",
                correlation_id=correlation_id,
                status=404,
            )

        if user.role != "CLINICIAN":
            return api_error(
                code="FORBIDDEN",
                message="Only clinicians can record follow-up contacts.",
                correlation_id=correlation_id,
                status=403,
            )

        if patient.facility.facility_id != user.facility_id:
            return api_error(
                code="FORBIDDEN",
                message="Clinicians can only update their own facility.",
                correlation_id=correlation_id,
                status=403,
            )

        serializer = FollowUpContactSerializer(data=request.data)

        if not serializer.is_valid():
            return api_error(
                code="INVALID_REQUEST",
                message="Invalid contact details.",
                correlation_id=correlation_id,
                status=400,
            )

        with transaction.atomic():
            FollowUpContact.objects.create(
                patient=patient,
                contacted_at=serializer.validated_data["contacted_at"],
                note=serializer.validated_data["note"],
            )

        logger.info(
            "Follow-up contact recorded",
            extra={
                "correlation_id": correlation_id,
                "patient_id": patient.id,
                "facility_id": patient.facility.facility_id,
                "role": user.role,
            },
        )

        return Response(status=status.HTTP_204_NO_CONTENT)