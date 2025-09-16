from ninja import NinjaAPI

from company_ninja_crud.api import employee_api
from company_ninja_crud.auth import DummyAuthBearer

api = NinjaAPI(
    auth=DummyAuthBearer(),
    title="Company Ninja CRUD API",
    version="1.0.0",
    urls_namespace="ninja_crud",
)

api.add_router("/employees", employee_api.router)
