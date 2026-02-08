# -*- coding: utf-8 -*-
"""PRND legacy *oldforms* compatibility.

This project was originally built on Django's pre-1.0 "oldforms" API:
    from django import forms
    from django.core import validators

and then used:
    class SomeForm(forms.Manipulator):
        self.fields = (... forms.TextField(...), ...)

Modern Django doesn't have these classes. Rewriting all templates and all
business logic to modern ``django.forms`` would be possible but invasive.

Instead, we provide a small subset of the old API that is enough for PRND's
templates and view logic:
- Manipulator with get_validation_errors/do_html2python
- Field classes: TextField, PasswordField, EmailField, LargeTextField,
  SelectField, CheckboxField, IntegerField, FloatField
- FormWrapper that templates render as ``{{ form.field }}``

This is NOT a general drop-in replacement for oldforms.
"""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

from django.utils.safestring import mark_safe

from . import validators


class Field:
    input_type: str = "text"

    def __init__(
        self,
        field_name: str,
        length: int = 30,
        maxlength: Optional[int] = None,
        is_required: bool = False,
        validator_list: Optional[Sequence[Callable[[Any, Dict[str, Any]], None]]] = None,
        member_name: Optional[str] = None,
        **kwargs: Any,
    ):
        self.field_name = field_name
        self.length = int(length) if length is not None else 30
        self.maxlength = int(maxlength) if maxlength is not None else None
        self.is_required = bool(is_required)
        self.validator_list = list(validator_list or [])
        self.member_name = member_name
        # accept and ignore extra kwargs used by oldforms (e.g. rows/cols)
        self.extra = kwargs

    def html2python(self, data: Any) -> Any:
        return data

    def python2html(self, data: Any) -> str:
        if data is None:
            return ""
        return str(data)

    def validate(self, field_data: Any, all_data: Dict[str, Any]) -> None:
        if self.is_required and field_data in (None, ""):
            raise validators.ValidationError("Это поле обязательно.")
        for v in self.validator_list:
            v(field_data, all_data)

    def render(self, value: Any) -> str:
        val = self.python2html(value)
        attrs = {
            "type": self.input_type,
            "name": self.field_name,
            "value": val,
        }
        if self.length:
            attrs["size"] = str(self.length)
        if self.maxlength is not None:
            attrs["maxlength"] = str(self.maxlength)
        return "<input %s/>" % " ".join(f'{k}="{escape(str(v))}"' for k, v in attrs.items())


class TextField(Field):
    input_type = "text"


class PasswordField(Field):
    input_type = "password"


class EmailField(TextField):
    # we keep it as text to preserve old behaviour
    pass


class LargeTextField(Field):
    def render(self, value: Any) -> str:
        val = escape(self.python2html(value))
        rows = int(self.extra.get("rows", 10))
        cols = int(self.extra.get("cols", 60))
        maxlength = self.maxlength
        # maxlength isn't standard on textarea, but keep it if present.
        attrs = {
            "name": self.field_name,
            "rows": str(rows),
            "cols": str(cols),
        }
        if maxlength is not None:
            attrs["maxlength"] = str(maxlength)
        return "<textarea %s>%s</textarea>" % (
            " ".join(f'{k}="{escape(str(v))}"' for k, v in attrs.items()),
            val,
        )


class SelectField(Field):
    def __init__(self, field_name: str, choices: Sequence[Tuple[Any, str]] = (), **kwargs: Any):
        super().__init__(field_name, **kwargs)
        self.choices = list(choices)

    def render(self, value: Any) -> str:
        current = "" if value is None else str(value)
        opts: List[str] = []
        for v, label in self.choices:
            vs = "" if v is None else str(v)
            selected = " selected=\"selected\"" if vs == current else ""
            opts.append(
                f"<option value=\"{escape(vs)}\"{selected}>{escape(str(label))}</option>"
            )
        return f"<select name=\"{escape(self.field_name)}\">" + "".join(opts) + "</select>"


class CheckboxField(Field):
    def __init__(self, field_name: str, checked_by_default: bool = False, **kwargs: Any):
        super().__init__(field_name, **kwargs)
        self.checked_by_default = bool(checked_by_default)

    def html2python(self, data: Any) -> bool:
        if data in (True, False):
            return bool(data)
        if data is None:
            return False
        s = str(data).lower()
        return s in ("1", "true", "on", "yes")

    def render(self, value: Any) -> str:
        checked = self.html2python(value)
        if value in (None, "") and self.checked_by_default:
            checked = True
        attrs = {
            "type": "checkbox",
            "name": self.field_name,
            "value": "1",
        }
        if checked:
            attrs["checked"] = "checked"
        return "<input %s/>" % " ".join(f'{k}="{escape(str(v))}"' for k, v in attrs.items())


class IntegerField(TextField):
    def __init__(self, *args: Any, **kwargs: Any):
        validator_list = list(kwargs.pop("validator_list", []) or [])
        validator_list = [self._is_integer] + validator_list
        kwargs["validator_list"] = validator_list
        super().__init__(*args, **kwargs)

    def _is_integer(self, field_data: Any, all_data: Dict[str, Any]) -> None:
        s = "" if field_data is None else str(field_data)
        if s == "":
            return
        if not s.lstrip("-").isdigit():
            raise validators.ValidationError("Введите число")

    def html2python(self, data: Any) -> Optional[int]:
        if data in (None, ""):
            return None
        return int(data)


class FloatField(TextField):
    def __init__(self, *args: Any, **kwargs: Any):
        validator_list = list(kwargs.pop("validator_list", []) or [])
        validator_list = [self._is_float] + validator_list
        kwargs["validator_list"] = validator_list
        super().__init__(*args, **kwargs)

    def _is_float(self, field_data: Any, all_data: Dict[str, Any]) -> None:
        s = "" if field_data is None else str(field_data)
        if s == "":
            return
        try:
            float(s.replace(",", "."))
        except ValueError:
            raise validators.ValidationError("Введите число")

    def html2python(self, data: Any) -> Optional[float]:
        if data in (None, ""):
            return None
        return float(str(data).replace(",", "."))


class Manipulator:
    fields: Sequence[Field] = ()

    def get_validation_errors(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        errors: Dict[str, List[str]] = {}
        # ensure data is a plain dict-like
        for f in self.fields:
            raw = data.get(f.field_name, "")
            # For checkbox, absence means unchecked
            if isinstance(f, CheckboxField) and f.field_name not in data:
                raw = ""
            try:
                f.validate(raw, data)
            except (validators.CriticalValidationError, validators.ValidationError) as e:
                errors.setdefault(f.field_name, []).extend(e.messages)
        return errors

    def do_html2python(self, data: Dict[str, Any]) -> None:
        for f in self.fields:
            raw = data.get(f.field_name, "")
            if isinstance(f, CheckboxField) and f.field_name not in data:
                raw = ""
            data[f.field_name] = f.html2python(raw)


class _BoundField:
    def __init__(self, field: Field, data: Dict[str, Any], errors: Dict[str, List[str]]):
        self.field = field
        self._data = data
        self._errors = errors

    @property
    def errors(self) -> List[str]:
        return self._errors.get(self.field.field_name, [])

    @property
    def html_error_list(self) -> str:
        if not self.errors:
            return ""
        lis = "".join(f"<li>{escape(e)}</li>" for e in self.errors)
        return mark_safe(f"<ul class=\"errorlist\">{lis}</ul>")

    def __str__(self) -> str:
        val = self._data.get(self.field.field_name, "")
        return mark_safe(self.field.render(val))


class FormWrapper:
    """Template helper to render oldforms-style manipulators."""

    def __init__(self, manipulator: Manipulator, data: Dict[str, Any], errors: Dict[str, List[str]]):
        self._manipulator = manipulator
        self._data = data
        self._errors = errors

    def __getattr__(self, name: str) -> _BoundField:
        for f in self._manipulator.fields:
            if f.field_name == name:
                return _BoundField(f, self._data, self._errors)
        raise AttributeError(name)
