from __future__ import annotations

from django.contrib import admin
from django.urls import re_path

from prnd.activity import views as activity_views
from prnd.calculator import views as calculator_views
from prnd.register import views as register_views

from django.shortcuts import redirect

def acts_year_redirect(request, act_name, year):
    return redirect(f"/prnd/all/{act_name}/{year}/", permanent=False)

def acts_user_redirect(request, act_name, userid):
    return redirect(f"/prnd/{act_name}/{userid}/", permanent=False)

def acts_user_add_redirect(request, act_name, userid):
    return redirect(f"/prnd/{act_name}/{userid}/add/", permanent=False)

def acts_obj_redirect(request, act_name, userid, act_id):
    return redirect(f"/prnd/{act_name}/{userid}/{act_id}/", permanent=False)

def acts_obj_delete_redirect(request, act_name, userid, act_id):
    return redirect(f"/prnd/{act_name}/{userid}/{act_id}/delete/", permanent=False)



acts_patterns = [
    re_path(r"^acts/(?P<act_name>\w+)/(?P<userid>\d+)/(?P<act_id>\d+)/delete/$", acts_obj_delete_redirect),
    re_path(r"^acts/(?P<act_name>\w+)/(?P<userid>\d+)/(?P<act_id>\d+)/$", acts_obj_redirect),
    re_path(r"^acts/(?P<act_name>\w+)/(?P<userid>\d+)/add/$", acts_user_add_redirect),
    re_path(r"^acts/(?P<act_name>\w+)/(?P<userid>\d+)/$", acts_user_redirect),
    re_path(r"^acts/(?P<act_name>\w+)/(?P<year>\d+)/$", acts_year_redirect),
]

#urlpatterns = acts_patterns + urlpatterns


urlpatterns = acts_patterns + [
    # Admin
    re_path(r"^prnd/admin/", admin.site.urls),

    # Auth
    re_path(r"^prnd/accounts/login/$", register_views.login_view, name="login"),

    # Registration / profile
    re_path(r"^prnd/change/$", register_views.change),
    re_path(r"^prnd/register/$", register_views.register),
    re_path(r"^prnd/confirm/(\w+)/$", register_views.confirm),
    re_path(r"^prnd/change/(\w+)/$", register_views.change_forgot),
    re_path(r"^prnd/profile/$", register_views.profile),
    re_path(r"^prnd/profile/(?P<id>\d+)/$", register_views.modify_profile),
    re_path(r"^prnd/profile/(?P<id>\d+)/delete/$", register_views.delete_profile),
    re_path(r"^prnd/forgot/$", register_views.forgot),

    # Calculator
    re_path(r"^prnd/sjournal/$", calculator_views.sjournal_list),
    re_path(r"^prnd/sjournal/add/$", calculator_views.new_sjournal_modify),
    re_path(r"^prnd/sjournal/(?P<id>\d+)/$", calculator_views.new_sjournal_modify),
    re_path(r"^prnd/sjournal/(?P<id>\d+)/delete/$", calculator_views.delete),
    re_path(r"^prnd/sjournal/add_list/(?P<list_name>\w+)/$", calculator_views.add_sjournals_list),

    # Activity
    re_path(r"^prnd/logout/$", activity_views.logout_view),
    re_path(r"^prnd/cur_user_attestation/$", activity_views.cur_user_attestation),
    re_path(r"^prnd/user_attestation/(?P<userid>\d+)/$", activity_views.user_attestation),
    re_path(r"^prnd/user_reports/$", activity_views.user_reports),
    re_path(r"^prnd/user_report/(?P<userid>\d+)/$", activity_views.user_report),
    re_path(r"^prnd/year_reports/(?P<userid>\d+)/(?P<year>\d+)/wb/$", activity_views.wbyear_reports),
    re_path(r"^prnd/year_reports/(?P<userid>\d+)/(?P<year>\d+)/$", activity_views.year_reports),
    re_path(r"^prnd/cur_user_year_report/(?P<year>\d+)/$", activity_views.cur_user_year_report),
    re_path(r"^prnd/all_user_reports/$", activity_views.all_user_reports),
    re_path(r"^prnd/full_statistics/$", activity_views.full_statistics),
    re_path(r"^prnd/accounts/profile/$", activity_views.main),
    re_path(r"^prnd/laboratory/(?P<userid>\d+)/(?P<year>\d+)/$", activity_views.laboratory_act_list),
    re_path(r"^prnd/all/(?P<act_name>\w+)/(?P<year>\d+)/$", activity_views.all_year_acts),
    re_path(r"^prnd/personal_menu/$", activity_views.personal_menu),
    re_path(r"^prnd/$", activity_views.main),

    re_path(r"^prnd/(?P<act_name>\w+)/(?P<userid>\d+)/$", activity_views.user_activity_index),
    re_path(r"^prnd/(?P<act_name>\w+)/$", activity_views.activity_index),
    re_path(r"^prnd/(?P<act_name>\w+)/(?P<userid>\d+)/add/$", activity_views.modify),
    re_path(r"^prnd/(?P<act_name>\w+)/(?P<userid>\d+)/(?P<act_id>\d+)/$", activity_views.modify),
    re_path(r"^prnd/(?P<act_name>\w+)/(?P<userid>\d+)/(?P<act_id>\d+)/delete/$", activity_views.delete),
]
