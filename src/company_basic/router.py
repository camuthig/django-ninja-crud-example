from ninja import NinjaAPI

from company_basic.api import employee_api
from company_basic.auth import DummyAuthBearer

api = NinjaAPI(auth=DummyAuthBearer())

api.add_router("/employees", employee_api.router)
