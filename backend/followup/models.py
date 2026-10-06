from django.db import models


class Facility(models.Model):
    facility_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    district = models.CharField(max_length=100)

    class Meta:
        ordering = ["facility_id"]

    def __str__(self):
        return f"{self.facility_id} - {self.name}"


class Patient(models.Model):
    class Sex(models.TextChoices):
        FEMALE = "female", "Female"
        MALE = "male", "Male"
        OTHER = "other", "Other"

    facility = models.ForeignKey(
        Facility,
        on_delete=models.PROTECT,
        related_name="patients",
    )
    patient_number = models.CharField(max_length=50)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    sex = models.CharField(max_length=10, choices=Sex.choices)
    phone_number = models.CharField(max_length=30, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["facility", "patient_number"],
                name="unique_patient_number_per_facility",
            )
        ]
        indexes = [
            models.Index(fields=["facility", "last_name", "first_name"]),
        ]

    def __str__(self):
        return f"{self.patient_number} - {self.first_name} {self.last_name}"


class Visit(models.Model):
    class VisitType(models.TextChoices):
        ROUTINE = "routine", "Routine"
        FOLLOW_UP = "follow_up", "Follow-up"
        UNSCHEDULED = "unscheduled", "Unscheduled"

    patient = models.ForeignKey(
        Patient,
        on_delete=models.PROTECT,
        related_name="visits",
    )
    visit_date = models.DateField()
    next_appointment_date = models.DateField(null=True, blank=True)
    visit_type = models.CharField(max_length=20, choices=VisitType.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-visit_date", "-id"]
        indexes = [
            models.Index(fields=["patient", "-visit_date"]),
            models.Index(fields=["next_appointment_date"]),
        ]

    def __str__(self):
        return f"{self.patient} - {self.visit_date}"