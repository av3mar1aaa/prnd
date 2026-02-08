# -*- coding: utf-8 -*-

from __future__ import annotations

from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Activation data for newly created users.

    Table already exists in the legacy SQLite database.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    activation_key = models.CharField(max_length=40)
    key_expires = models.DateTimeField()

    class Meta:
        managed = False

    def __str__(self) -> str:
        return f"UserProfile({self.user_id})"
