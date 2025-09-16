from datetime import date

from ninja import Router
from ninja import Schema
from ninja_crud import views
from ninja_crud import viewsets
from pydantic import Field, ConfigDict

from company_ninja_crud.models import Employee

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
    # If we use `department` instead here, then it expects a `Department` object, not an ID.
    projects: list[int] = Field(..., alias="project_ids")
    # The Pydantic fields must exactly match the model fields, but we want to keep our APIs consistent in using `_id`
    # Therefore we use the `alias` parameter to map the field name to the model field name.
    birthdate: date = None

    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True)
    # `from_attributes` is "ORM" mode and default in Ninja
    # `str_strip_whitespace` tells Pydantic to strip leading and trailing whitespace from strings

class EmployeeUpdateRequest(Schema):
    first_name: str = None
    last_name: str = None
    department_id: int = None
    # If we use `department` instead here, then it expects a `Department` object, not an ID.
    projects: list[int] = Field(None, alias="project_ids")
    # The Pydantic fields must exactly match the model fields, but we want to keep our APIs consistent in using `_id`
    # Therefore we use the `alias` parameter to map the field name to the model field name.
    birthdate: date = None


    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True)
    # `from_attributes` is "ORM" mode and default in Ninja
    # `str_strip_whitespace` tells Pydantic to strip leading and trailing whitespace from strings


class EmployeeViewSet(viewsets.APIViewSet):
    api = router
    model = Employee
    default_response_body = EmployeeResponse
    default_request_body = EmployeeRequest

    list_departments = views.ListView()
    create_department = views.CreateView()
    read_department = views.ReadView()
    update_department = views.UpdateView(request_body=EmployeeUpdateRequest, methods=["PATCH"])
    delete_department = views.DeleteView()
