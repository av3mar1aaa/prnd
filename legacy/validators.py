# -*- coding: utf-8 -*-
"""PRND legacy validators.

The original codebase was written for Django's *oldforms* system (pre-Django 1.0),
using ``django.core.validators``.

Modern Django removed that module/API, so we provide a minimal compatible subset
that is used by this project.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable, Iterable, List, Optional


class ValidationError(Exception):
    """Validation error compatible with oldforms.

    The legacy code sometimes expects ``e.messages`` to exist.
    """

    def __init__(self, message: Any):
        if isinstance(message, (list, tuple)):
            self.messages = [str(m) for m in message]
        else:
            self.messages = [str(message)]
        super().__init__(self.messages)


class CriticalValidationError(ValidationError):
    """In oldforms, CriticalValidationError stopped further validation.

    In this project we treat it as a regular ValidationError.
    """


def isAlphaNumeric(field_data: Any, all_data: dict) -> None:
    """Legacy: allow only latin letters, digits and underscore."""

    s = "" if field_data is None else str(field_data)
    if not re.fullmatch(r"[0-9A-Za-z_]+", s):
        raise ValidationError("Разрешены только латинские буквы, цифры и _. ")


@dataclass
class AlwaysMatchesOtherField:
    other_field: str
    message: str

    def __call__(self, field_data: Any, all_data: dict) -> None:
        if field_data != all_data.get(self.other_field, ""):
            raise ValidationError(self.message)


@dataclass
class RequiredIfOtherFieldEquals:
    other_field: str
    other_value: Any
    message: str

    def __call__(self, field_data: Any, all_data: dict) -> None:
        if str(all_data.get(self.other_field, "")) == str(self.other_value):
            if field_data in (None, ""):
                raise ValidationError(self.message)


@dataclass
class RequiredIfOtherFieldDoesNotEqual:
    other_field: str
    other_value: Any
    message: str

    def __call__(self, field_data: Any, all_data: dict) -> None:
        if str(all_data.get(self.other_field, "")) != str(self.other_value):
            if field_data in (None, ""):
                raise ValidationError(self.message)


@dataclass
class RequiredIfOtherFieldNotGiven:
    other_field: str
    message: str = "Это поле обязательно."

    def __call__(self, field_data: Any, all_data: dict) -> None:
        other = all_data.get(self.other_field, "")
        if other in (None, "") and field_data in (None, ""):
            raise ValidationError(self.message)


# Convenience alias used in a couple of places
AlwaysMatchesOtherField = AlwaysMatchesOtherField
RequiredIfOtherFieldEquals = RequiredIfOtherFieldEquals
RequiredIfOtherFieldDoesNotEqual = RequiredIfOtherFieldDoesNotEqual
RequiredIfOtherFieldNotGiven = RequiredIfOtherFieldNotGiven
