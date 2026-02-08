# -*- coding: utf-8 -*-
"""Legacy shortcuts.

The project uses ``django.shortcuts.render_to_response`` heavily.
That helper was deprecated and eventually removed.

We provide a small wrapper compatible with the old call sites:
    render_to_response(template_name, context_dict)

If a request is available, prefer using ``django.shortcuts.render``.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from django.http import HttpRequest, HttpResponse
from django.template import loader


def render_to_response(
    template_name: str,
    context: Optional[Dict[str, Any]] = None,
    request: Optional[HttpRequest] = None,
) -> HttpResponse:
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context or {}, request))
