from datetime import date

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja import Schema
from ninja.pagination import paginate
from pydantic import ConfigDict

from company_basic.models import Employee

router = Router()


class EmployeeResponse(Schema):
    id: int
    first_name: str
    last_name: str
    department_id: int = None
    project_ids: list[int]
    birthdate: date = None

    @staticmethod
    def resolve_project_ids(obj: Employee):
        return [p.id for p in obj.projects.all()]


class EmployeeRequest(Schema):
    first_name: str
    last_name: str
    department_id: int = None
    project_ids: list[int] = []
    birthdate: date = None

    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True)
    # `from_attributes` is "ORM" mode and default in Ninja
    # `str_strip_whitespace` tells Pydantic to strip leading and trailing whitespace from strings


@router.get("/", response=list[EmployeeResponse])
@paginate
def get_employees(request):
    return Employee.objects.prefetch_related("projects").all()


@router.post("/", response={201: EmployeeResponse})
def create_employee(request, data: EmployeeRequest):
    employee = Employee.objects.create(
        first_name=data.first_name,
        last_name=data.last_name,
        department_id=data.department_id,
        birthdate=data.birthdate,
    )

    employee.projects.set(data.project_ids)

    return employee


@router.get("/{id}", response=EmployeeResponse)
def get_employee(request, id: int):
    return get_object_or_404(Employee.objects.prefetch_related("projects"), id=id)


class EmployeeUpdateRequest(Schema):
    first_name: str = None
    last_name: str = None
    department_id: int = None
    project_ids: list[int] = None
    birthdate: date = None

    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True)
    # `from_attributes` is "ORM" mode and default in Ninja
    # `str_strip_whitespace` tells Pydantic to strip leading and trailing whitespace from strings

@router.patch("/{id}", response=EmployeeResponse)
def update_employee(request, id: int, data: EmployeeUpdateRequest):
    instance = get_object_or_404(Employee.objects.prefetch_related("projects"), id=id)

    provided_data = data.model_dump(exclude_unset=True)

    instance.first_name = provided_data.get("first_name", instance.first_name)
    instance.last_name = provided_data.get("last_name", instance.last_name)
    instance.department_id = provided_data.get("department_id", instance.department_id)
    instance.birthdate = provided_data.get("birthdate", instance.birthdate)

    instance.save()

    if project_ids := provided_data.get("project_ids", None):
        instance.projects.set(project_ids)

    return instance


@router.delete("/{id}", response={204: None})
def delete_employee(request, id: int):
    get_object_or_404(Employee, id=id).delete()

    return 204, ""
