from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(
        self,
        email="",
        username="",
        full_name="",
        password=None,
        is_staff=False,
        is_active=True,
        **extra_fields,
    ):
        if not password:
            raise ValueError("User should have password.")

        user = self.model(
            email=email,
            username=username,
            full_name=full_name,
            is_active=is_active,
            is_staff=is_staff,
            **extra_fields,
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        user = self.model(
            username=username,
            email=email,
            is_active=True,
            is_staff=True,
            is_superuser=True,
            **extra_fields,
        )
        user.set_password(password)
        user.save()
        return user


class User(AbstractUser):
    full_name = models.CharField(_("Full name"), max_length=150, blank=True)
    objects = UserManager()
