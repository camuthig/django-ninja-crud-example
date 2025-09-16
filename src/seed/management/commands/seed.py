from datetime import date

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from company_basic import models as basic_models
from company_ninja_crud import models as ninja_crud_models


class Command(BaseCommand):
    def handle(self, *args, **options):
        get_user_model().objects.create_user("testuser")

        self.stdout.write(self.style.SUCCESS("Successfully created testuser"))

        self._seed_basic_app()
        self._seed_ninja_crud_app()

        self.stdout.write(self.style.SUCCESS("Successfully seeded. You can now use authorize using the key 'supersecret:1'"))

    def _seed_basic_app(self):
        self.stdout.write("Creating models for basic Ninja app...")

        growth_department = basic_models.Department.objects.create(title="Growth")
        infrastructure_department = basic_models.Department.objects.create(title="Infrastructure")

        growth_project = basic_models.Project.objects.create(title="Growth Project", department=growth_department)
        infrastructure_project = basic_models.Project.objects.create(
            title="Infrastructure Project", department=infrastructure_department
        )

        employee = basic_models.Employee.objects.create(
            first_name="Bob",
            last_name="Smith",
            department=growth_department,
            birthdate=date.today(),
        )

        employee.projects.set([growth_project, infrastructure_project])


        self.stdout.write(self.style.SUCCESS("Successfully created models"))

    def _seed_ninja_crud_app(self):
        self.stdout.write("Creating models for the Ninja CRUD app...")

        growth_department = ninja_crud_models.Department.objects.create(title="Growth")
        infrastructure_department = ninja_crud_models.Department.objects.create(title="Infrastructure")

        growth_project = ninja_crud_models.Project.objects.create(title="Growth Project", department=growth_department)
        infrastructure_project = ninja_crud_models.Project.objects.create(
            title="Infrastructure Project", department=infrastructure_department
        )

        employee = ninja_crud_models.Employee.objects.create(
            first_name="Bob",
            last_name="Smith",
            department=growth_department,
            birthdate=date.today(),
        )

        employee.projects.set([growth_project, infrastructure_project])

        self.stdout.write(self.style.SUCCESS("Successfully created models"))
