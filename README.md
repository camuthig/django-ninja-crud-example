# CRUD APIs with Django Ninja

This is an example Django project that demonstrates how to use Django Ninja to create a CRUD API.

It builds on the [Django Ninja CRUD tutoria](https://django-ninja.dev/tutorial/other/crud/), and it is recommended to
start there.

The `company_basic` and `company_django_ninja` implement the same models and behaviors. The basic project only uses the
concepts built into Django Ninja out of the box. The `company_django_ninja` project explores the capabilities of the
[Django Ninja CRUD](https://github.com/hbakri/django-ninja-crud) package to accomplish the same thing.

To manually test the APIs

1. Migrate the database with `uv run manage.py migrate`
2. Seed the database with `uv run manage.py seed`
3. Run the server with `uv run manage.py runserver`
4. Visit http://localhost:8000/basic/docs/
5. In "Authorize" on the docs page, use the key "supersecret:1"
6. The built-in API client in the documentation should work now!
7. Visit http://localhost:8000/ninja-crud/docs/
8. Use the same key and do it all again!
