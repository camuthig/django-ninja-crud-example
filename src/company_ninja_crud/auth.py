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
