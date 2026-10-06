from rest_framework import serializers

from .models import Visit


class FollowUpSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="patient.id")
    patient_number = serializers.CharField(source="patient.patient_number")
    first_name = serializers.CharField(source="patient.first_name")
    last_name = serializers.CharField(source="patient.last_name")
    facility_id = serializers.CharField(source="patient.facility.facility_id")
    facility_name = serializers.CharField(source="patient.facility.name")
    missed_appointment_date = serializers.DateField(
        source="next_appointment_date"
    )
    days_overdue = serializers.SerializerMethodField()
    follow_up_status = serializers.SerializerMethodField()
    phone_number = serializers.CharField(source="patient.phone_number")
    last_contact_attempt = serializers.SerializerMethodField()

    class Meta:
        model = Visit
        fields = [
            "id",
            "patient_number",
            "first_name",
            "last_name",
            "facility_id",
            "facility_name",
            "missed_appointment_date",
            "days_overdue",
            "follow_up_status",
            "phone_number",
            "last_contact_attempt",
        ]

    def get_days_overdue(self, obj):
        from django.utils import timezone

        return (timezone.localdate() - obj.next_appointment_date).days

    def get_follow_up_status(self, obj):
        days_overdue = self.get_days_overdue(obj)

        if days_overdue > 0:
            return "overdue"

        return "due_soon"

    def get_last_contact_attempt(self, obj):
        return None