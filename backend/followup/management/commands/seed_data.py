from datetime import date

from django.core.management.base import BaseCommand

from followup.models import Facility, Patient, Visit


class Command(BaseCommand):
    help = "Seed CareLink assessment data."

    def handle(self, *args, **options):
        facilities = {}

        facility_data = [
            ("FAC-0101", "Mwansa Urban Clinic", "Mwansa"),
            ("FAC-0207", "Kalemba Rural Health Centre", "Kalemba"),
            ("FAC-0312", "Chembe District Hospital", "Chembe"),
        ]

        for facility_id, name, district in facility_data:
            facility, _ = Facility.objects.update_or_create(
                facility_id=facility_id,
                defaults={
                    "name": name,
                    "district": district,
                },
            )
            facilities[facility_id] = facility

        thandiwe, _ = Patient.objects.update_or_create(
            facility=facilities["FAC-0101"],
            patient_number="P-0101-0001",
            defaults={
                "first_name": "Thandiwe",
                "last_name": "Banda",
                "date_of_birth": date(1990, 4, 12),
                "sex": Patient.Sex.FEMALE,
                "phone_number": "0977000001",
            },
        )

        mulenga, _ = Patient.objects.update_or_create(
            facility=facilities["FAC-0207"],
            patient_number="P-0207-0001",
            defaults={
                "first_name": "Mulenga",
                "last_name": "Phiri",
                "date_of_birth": date(1985, 8, 20),
                "sex": Patient.Sex.MALE,
                "phone_number": "0977000002",
            },
        )

        chipo, _ = Patient.objects.update_or_create(
            facility=facilities["FAC-0312"],
            patient_number="P-0312-0001",
            defaults={
                "first_name": "Chipo",
                "last_name": "Zulu",
                "date_of_birth": date(1995, 2, 5),
                "sex": Patient.Sex.FEMALE,
                "phone_number": "0977000003",
            },
        )

        Visit.objects.update_or_create(
            patient=thandiwe,
            visit_date=date(2026, 8, 20),
            defaults={
                "next_appointment_date": date(2026, 9, 5),
                "visit_type": Visit.VisitType.ROUTINE,
            },
        )

        Visit.objects.update_or_create(
            patient=mulenga,
            visit_date=date(2026, 8, 25),
            defaults={
                "next_appointment_date": date(2026, 9, 10),
                "visit_type": Visit.VisitType.FOLLOW_UP,
            },
        )

        Visit.objects.update_or_create(
            patient=chipo,
            visit_date=date(2026, 9, 30),
            defaults={
                "next_appointment_date": None,
                "visit_type": Visit.VisitType.ROUTINE,
            },
        )

        self.stdout.write(
            self.style.SUCCESS(
                "CareLink assessment data seeded successfully."
            )
        )