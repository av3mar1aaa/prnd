# -*- coding: utf-8 -*-
"""Tiny compatibility helpers.

The legacy project bundled helpers named ``login_required`` and ``IntegerField``.
In modern Django, ``login_required`` comes from
``django.contrib.auth.decorators``.

We keep the same import paths to avoid touching too much code.
"""

from __future__ import annotations

from django.contrib.auth.decorators import login_required as _login_required

from prnd.legacy.forms import IntegerField  # noqa: F401  (re-export)

# Re-export with the old name
login_required = _login_required
