# Building CRUD APIs with Django Ninja

Serving JSON APIs is a common pattern in the world of single page (SPA) and mobile application development.
The most common of these use cases is to support CRUD (create/read/update/delete) operations using JSON representations
of models.

Django Ninja is a Django package that makes it possible to build APIs using a function-based programming style 
similar to Express in the NodeJS world. These are written as function-based views, with a function for each
route on your application. Serialization and deserialization are implemented using Pydantic classes. These types provide
a mechanism for annotating the Python objects and automatically generating API documentation.

In this post we are going to explore how to write an API-first Django application using Django Ninja.

This guide is going to build on top of the [CRUD example](https://django-ninja.dev/tutorial/other/crud/) in the Django Ninja documentation. So first things first,
give that a review and learn the basics of Django Ninja.

I'll wait...

Great! Now let's get started.

Having reviewed the CRUD example, you can see that Django Ninja provides the API layer out of the box. It does not
have any opinions on many common parts of a Django application like retrieving models from the database, saving models,
 permissions, etc. That is handled by the application developer instead. This may seem verbose, and results in more
lines of code, but it also can be seen as Ninja not doing too much, allowing us to build our applications the way we need to.

You can find the final code for this example in this [repository](https://github.com/camuthig/django-ninja-crud-example).

So let's expand on the example to show a few extra concepts.

## Dealing with ManyToMany Fields

The first thing we can do is extend our model to include a `ManyToManyField`. This is an important concept because they
behave differently than the `ForeignKey` field in regard to how the data gets saved and updated. We'll add a new `Project`
model to our application and say that our users can be assigned to multiple projects.

```python
# file: src/company_basic/models.py
from django.db import models

class Department(models.Model):
    title = models.CharField(max_length=100)
    
class Project(models.Model):
    title = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birthdate = models.DateField(null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    projects = models.ManyToManyField(Project)
```

### Adding Resolvers to the Output

Now we can update our output schema to include the new project IDs field. Because this is not a direct field on our
model, we will need to define a resolver for it.

```python
# file: src/company_basic/api/employee_api.py
from ninja import Schema
from pydantic import Field
from datetime import date

class EmployeeResponse(Schema):
    id: int
    first_name: str
    last_name: str
    department_id: int = None
    project_ids: list[int]
    birthdate: date = None

    @staticmethod
    def resolve_project_ids(obj):
        return [p.id for p in obj.projects.all()]
```

Bonus tip here: make sure you are prefetching the `project_ids` field in your queries, at least the list query, to avoid
N+1 queries. `Employee.objects.prefetch_related("projects").all()`

### Handling ManyToMany Writes

We also need to update how we handle the data in our `POST` view now, since `ManyToManyField`s are not handled directly
written to as a property. You can also see that we are shifting our code for creating the `Employee` to be more explicit
instead of just using `**data.dict()`. This makes it more clear what we are doing, and makes the explicit handling of the
project IDs easier. If you do want to use the `dict` approach, I recommend using `data.model_dump(exclude={"projects"})`
to exclude the `projects` field from the output. The `dict` function shown in the Ninja example is deprecated in Pydantic
V2, and replaced with `model_dump`.

```python
class EmployeeRequest(Schema):
    first_name: str
    last_name: str
    department_id: int = None
    project_ids: list[int] = []
    birthdate: date = None

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
```

## Dealing With Partial Updates

Next, let's convert our `PUT` view to `PATCH` and support partial updates. `PUT` is often easier because it 
overwrites all the data, but the flexibility of `PATCH` proves more challenging. We'll create a new schema specific for
the `PATCH` operation and mark everything with a default `None` value. By doing this, the Pydantic types are still validated,
but the field is not required in the input. From there, we will convert the Pydantic instance into a dictionary with just
the provided fields using `model_dump(exclude_unset=True)`.

Again, we see here that everything becomes more explicit. We increase the number of lines but also gain flexibility
and clarity.

```python
class EmployeeUpdateRequest(Schema):
    first_name: str  = None
    last_name: str  = None
    department_id: int = None
    project_ids: list[int] = None
    birthdate: date  = None


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
```

## Modularizing and Registering the API

I recommend using separate files for each resource in your API to avoid having a single, giant file with everything in it.

Instead, create a file for each of your resources and colocate the schemas and views together in that file with a 
[`Router`](https://django-ninja.dev/guides/routers/). A router allows you to group certain APIs together and then
register them up with a single API. In our specific case, taking the Ninja example, we will replace `api = NinjaAPI()`
with `router = Router()` and use `router` for all of our view functions, as you may have already noticed hints of above.

```python
# file: src/company_basic/api/employee_api.py
from ninja import Router

router = Router()
```

Now we can register our router with the API. We'll do this by creating a central location in our Django application to
configure this at `src/company_basic/router.py`.

```python
# file: src/company_basic/router.py
from ninja import NinjaAPI
from company_basic.api import employee_api

api = NinjaAPI()

api.add_router("/employees", employee_api.router)
```

And then we add this API to our `urls.py` file.

```python
# file: src/core/urls.py
from django.contrib import admin
from django.urls import path

from company_basic.router import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
```

## Adding Authentication

Next, let's add authentication to our API. Ninja provides the building blocks for a number of different
[authentication backends](https://django-ninja.dev/guides/authentication/#available-auth-options) out of the box, and 
we'll use the `HttpBearer` as our example.

```python
# file: src/company_basic/auth.py
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from ninja.security import HttpBearer


class DummyAuthBearer(HttpBearer):
    def authenticate(self, request, token):
        # NOTE: This is not secure, or even robust, at all, just for demo purposes
        split = token.split(":")
        if len(split) != 2:
            # Return a "false" like response to fail this authentication step
            return

        token_value, user_id = split

        if token_value != "supersecret":
            return

        # On success, return the user
        # This must be "true" like, and Django Ninja will add this to the `request.auth` field.
        user = get_user_model().objects.filter(id=user_id).first()

        # This forces the user object onto the `request.user` property so that it is available for things like the
        # `permission_required` decorator.
        request.user = user or AnonymousUser()

        return user
```

I recommend registering authentication at the `NinjaAPI` level to ensure all of your views behave consistently. If you
need to be able to customize this, though, then you can add it at the `Router` level in the same way.

```python
# file: src/company_basic/router.py
from ninja import NinjaAPI
from company_basic.auth import DummyAuthBearer

api = NinjaAPI(auth=DummyAuthBearer())
```

The auth implementation should return a "false" like value on failure and a "true" like value on success.

The recommendation is that, on success, it should return a user. Whatever is returned will be added to the context of
the `request` object passed to your view as the `auth` property. So you can access it in any of your views with
`request.auth`.

## Adding Pagination

The final addition to make to our CRUD example is to paginate our list API. Django Ninja provides a `paginate` decorator
that will handle basic pagination for you. It automatically adds limit/offset query parameters and will wrap your 
response list with `items` and provide an additional `count` property.

```json
{
    "items": [],
    "count": 0
}
```

This works out of the box if you are returning a `QuerySet`, however, it is less friendly if you are generating a list
and returning it. It assumes that the returned value will either be a `QuerySet` or is a list that it can splice and take
a `len` on to get the count. If your requirements don't fit within this, things get a bit harder. I have solutions for
that as well, but they are outside of the scope of this tutorial.

## Permissions: A Missing Story

It is worth noting that Django Ninja does not provide a built-in mechanism for handling permissions. There have been some
discussions on this in the repository, but no clear path is set yet. I will try to dig into ways to work with permissions
in a later tutorial as well. For now, the best way to handle it is explicitly in your view functions. This could be done
using the built-in Django permissions system, for example:

```python
@router.post("/", response={201: EmployeeResponse})
def create_employee(request, data: EmployeeRequest):
    if not request.auth.has_perm("company_basic.add_employee"):
        raise PermissionDenied()
    # ... rest of the function
```

Unfortunately, because the Django Ninja authentication system adds the user to `request.auth` instead of `request.user`,
you cannot use the `permission_required` decorator provided by Django without making alterations somewhere. This can be
done within your implementation of the authentication backend, and an example of it is included in the 
[repository](https://github.com/camuthig/django-ninja-crud-example/blob/c78445213dc74b1b910b596580c556daf5de1093/src/company_basic/auth.py#L23-L25).
Then, the decorator can be added to any of the view functions.

```python
@router.get("/", response=list[EmployeeResponse])
@paginate
@permission_required("company_basic.view_employee")
def get_employees(request):
    return Employee.objects.prefetch_related("projects").all()
```

## Using a Library

If your primary use case is aligned with everything above, then it may be worth considering the [Django Ninja CRUD](https://github.com/hbakri/django-ninja-crud)
project. I have no production experience with the project yet, so I cannot personally endorse it. However, it is gaining a good
deal of popularity, and my explorations into the project were smooth and productive.

This is a project that extends on Django Ninja's core functionality to provide a declarative, class-based syntax for
efficiently configuring CRUD APIs. This should feel familiar to anyone used to working Django Rest Framework model viewsets,
but it is a notable shift from the Express-style implemented by the core Django Ninja library.

An example building the same APIs as above using Django Ninja CRUD is included in the 
[repository](https://github.com/camuthig/django-ninja-crud-example/blob/main/src/company_ninja_crud/api/employee_api.py) linked to this tutorial.


## A Fork in the Road: django-shinobi

A closing note about the state of Django Ninja.

In January 2025, a community member forked Django Ninja and created [django-shinobi](https://github.com/jaredhanson/django-shinobi).
This could be considered a "soft fork" primarily focused on including some community contributions into the project. It
uses the same namespaces as Django Ninja, but does not work with things like Django Ninja Extras or Django Ninja CRUD because
of conflicting dependencies. There are just a [few differences in the projects](https://pmdevita.github.io/django-shinobi/differences/)
as of writing this.

There is the possibility of Shinobi merging back into Ninja at some point in the future, or continuing to be a fork. 
I am unable to make a recommendation as to which is "better," at this time. Both are receiving a slow
stream of improvements, but they are different improvements. This difference in focus could prove to be great for both
projects in the future, or result in disparate communities.
