# -*- coding: utf-8 -*-

"""Email helpers.

The original project sent emails via direct SMTP calls (Python 2 modules
`rfc822`, `email.MIMEText`, etc.). For local development (and for portability),
we route everything through Django's email framework.

By default (see settings.py) emails are printed to the console.
"""

from __future__ import annotations

from django.core.mail import EmailMultiAlternatives

from prnd.activity.acttypes import (
    act_type_num,
    get_user_activity_list_on_given_year,
    get_activity_cost,
    type2rusname1,
    act2html,
)
from prnd.calculator.attributes import get_attribute
from prnd.activity.userreports import get_str_status_report

# Kept for compatibility with legacy links/templates
site = "http://localhost:8000/prnd"
mail = "prnd@example.invalid"


def send_mail(subject: str, email_body: str, from_email: str, recipient_list: list[str]) -> None:
    msg = EmailMultiAlternatives(subject=subject, body=email_body, from_email=from_email, to=recipient_list)
    msg.attach_alternative(email_body, "text/html")
    msg.send(fail_silently=True)


def gen_report_text(owner, year):
    typed_act_list = ""
    full_cost = 0.0
    for act_type in range(act_type_num):
        act_list = get_user_activity_list_on_given_year(owner, act_type, year)
        full_info_act_list = ""
        iterator = 0
        for act in act_list:
            iterator += 1
            cost = get_activity_cost(act_type, act)
            full_cost += cost
            new_str = (
                "<tr><td align=center>%d. </td><td align=left>%s</td>"
                "<td align=center>%f</td></td></tr>" % (iterator, act2html(act_type, act), cost)
            )
            full_info_act_list += new_str
        if iterator != 0:
            typed_act_list += (
                "<center><table border=1 align=center width=100%> "
                "    <tr><th width=10%>No</th><th>" + type2rusname1(act_type) + "</th>"
                "    <th width=10%>балл</th></tr>" + full_info_act_list + "</table></center>"
            )
    return typed_act_list


def send_report_to_user(user, owner, year):
    a = get_attribute(user)
    if not getattr(a, "email_verbose", False):
        return

    email_subject = "otchet pol'zovatelja %s za %d god" % (owner.username, int(year))
    head = (
        "<html><head><meta content=\"text/html\" http-equiv=\"content-type\" charset=UTF-8/>"
        "<title></title></head><body>Уважаемый %s %s!<br><br>"
        "Обращаем Ваше внимание на то, что статус отчета пользователя %s %s за %d год был изменен."
        % (user.last_name, user.first_name, owner.last_name, owner.first_name, int(year))
    )
    head += " Текущий статус отчета: %s." % (get_str_status_report(owner, year))
    head += "<br><br>Содержание отчета Вы можете просмотреть ниже или на сайте %s" % (site)
    head += "<br><br>"

    email_body = head + gen_report_text(owner, year) + "</body></html>"
    send_mail(email_subject, email_body, mail, [user.email])
