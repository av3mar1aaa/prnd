# This Python file uses the following encoding: utf-8
#from prnd.calculator.models import SelectedJournal
#from django.shortcuts import render_to_response, get_object_or_404
#from prnd.activity.models import *
#from prnd.activity.forms import *
#from prnd.calculator.models import *
#from django.core.exceptions import ObjectDoesNotExist
#from django.http import HttpResponse
#from decimal import *
from django.core.exceptions import ObjectDoesNotExist
from prnd.calculator.models import YearStatistics
from prnd.register.yearstat import *
from django.shortcuts       import get_object_or_404
from django.contrib.auth.models import User
from prnd.calculator.attributes import get_attribute 
from prnd.activity.acttypes import *

#def get_coef_modifier(user,year):
#  ys = get_user_yearstatistics(user,year)
#  return ys.coef_modifier

def is_admin(user):
  a = get_attribute(user)
  return a.is_admin
  
def is_zavlab(user):
  a = get_attribute(user)
  return a.is_zavlab
  
def is_lab_head(user):
  a = get_attribute(user)
  return a.is_headlab
  
def is_laboratory(user):
  a = get_attribute(user)
  return a.is_laboratory

def is_institute(user):
  a = get_attribute(user)
  return a.is_institute


def is_employee(user):
  a = get_attribute(user)
  return a.status == 'N'
  
def is_inst_head(user):
  a = get_attribute(user)
  return a.rank == 'D'
  
def get_user_weight(user):
  if is_laboratory(user):
    return 0.0

  if is_institute(user):
    return 0.0
    
  a = get_attribute(user)
  
  if a.status == 'L':
    return 0.0
  
  if a.status != 'N':
    return 0.0
#  else:
#    if a.rate == 0:
#      return 1.0
#    elif a.rate == 1:
#      return 0.9
#    elif a.rate == 2:
#      return 0.8
#    elif a.rate == 3:
#      return 0.75
#    elif a.rate == 4:
#      return 0.7
#    elif a.rate == 5:
#      return 0.6
#    elif a.rate == 6:
#      return 0.5
#    elif a.rate == 7:
#      return 0.4
#    elif a.rate == 8:
#      return 0.3
#    elif a.rate == 9:
#      return 0.25
#    elif a.rate == 10:
#      return 0.2
#    elif a.rate == 11:
#      return 0.1
#    elif a.rate == 12:
#      return 0.0
      
  return 1.0

def get_user_stavka(user):
  if is_laboratory(user):
    return 0.0
  if is_institute(user):
    return 0.0

  a = get_attribute(user)

  if a.status == 'L':
    return 0.0
  if a.status != 'N':
    return 0.0
  else: 
    if a.rate == 0: 
      return 1.0 
    elif a.rate == 1: 
      return 0.9 
    elif a.rate == 2: 
      return 0.8 
    elif a.rate == 3: 
      return 0.75 
    elif a.rate == 4: 
      return 0.7 
    elif a.rate == 5: 
      return 0.6 
    elif a.rate == 6: 
      return 0.5 
    elif a.rate == 7: 
      return 0.4 
    elif a.rate == 8: 
      return 0.3 
    elif a.rate == 9: 
      return 0.25 
    elif a.rate == 10: 
      return 0.2 
    elif a.rate == 11: 
      return 0.1 
    elif a.rate == 12: 
      return 0.0

  return 1.0
  
def is_simple_user(user):
  return not is_admin(user) and not is_zavlab(user) and not is_laboratory(user) and not is_institute(user)
  
# whether the first user is more powerful than the second one
def user_ge (id1, id2):
  id1 = int(id1)
  id2 = int(id2)

  if id1==id2:
    return True
    
  u1 = get_object_or_404(User, pk=id1)
  u2 = get_object_or_404(User, pk=id2)
  
  a1 = get_attribute(u1)
  if a1.is_admin:
    return True
    
  if not a1.is_zavlab:
    return False
    
  if u1.groups.all()[0] == u2.groups.all()[0]:
    return True
  
  return False

def is_report_submitted_by_user(user, year):
  ys = get_user_yearstatistics(user, year)
  return ys.status >= 1
    
def is_report_confirmed_by_zavlab(user, year):
  ys = get_user_yearstatistics(user, year)
  return ys.status >= 2

def is_report_confirmed_by_admin(user, year):
  ys = get_user_yearstatistics(user, year)
  return ys.status >= 3

def get_coef(user, year):
  year=int(year)
  try:
    ys = user.yearstatistics_set.get(year=year)
    return ys.coef_modifier
  except ObjectDoesNotExist:
    return 1.0
    
def get_maximal_report_status_choice(user):
  if is_admin(user):
    return 3
  elif is_zavlab(user):
    return 2
  else:
    return 1    

def get_report_status(user, year):
  ys = get_user_yearstatistics(user, year)
  return int(YearStatistics.STATUS_CHOICES[int(ys.status)][0])

def get_str_status_report(user, year):
  ys = get_user_yearstatistics(user, year)
  return YearStatistics.STATUS_CHOICES[int(ys.status)][1]
  
def get_str_short_status_report(user, year):
  ys = get_user_yearstatistics(user, year)
  return YearStatistics.STATUS_SHORT_CHOICES[int(ys.status)][1]
  
def get_user_detailed_report(user, year):
  ys = get_user_yearstatistics(user, year)
  return ys.detailed_report

def can_add_or_modify_activity(this_user_id, owner_id, year):
  this_user_id = int (this_user_id)
  owner_id     = int (owner_id    )
  year         = int (year        )
  
  this_user = get_object_or_404(User, pk=this_user_id)
  owner     = get_object_or_404(User, pk=owner_id    )
  
  if is_admin(this_user):
    return True
  
  if not user_ge(this_user_id, owner_id):
    return False
    
  if is_simple_user(this_user) and is_report_submitted_by_user(owner, year):
    return False
    
  if is_zavlab(this_user) and is_report_confirmed_by_zavlab(owner, year):
    return False
    
  if is_admin(this_user) and is_report_confirmed_by_admin(owner, year):
    return False
  
  return True
  
def get_user_year_cost(report_owner, year):  
  year = int(year)

  result = 0.0

  if is_lab_head(report_owner):
    result = get_head_user_year_cost(report_owner, year)
  else:
    result = get_simple_user_year_cost(report_owner, year)
    
  return round(result, 3)
  
def get_full_type_cost(report_owner, year, act_type):
  year = int(year)
  
  full_cost = 0.0
  act_list = get_user_activity_list_on_given_year(report_owner, act_type, year)
  
  if act_type != conference_type:
    for act in act_list:
      cost =  get_activity_cost(act_type, act)
      full_cost += cost
  else:
    # kulikov: izmeneno 03.02.2012
    # type03 = 0.0
    # type45 = 0.0
    for act in act_list:
      cost =  get_activity_cost(act_type, act)
      full_cost += cost
    
    if full_cost > 45.0:
       full_cost = 45.0
    #  if act.conftype <= 3:
    #     type03 += cost
    #  else:
    #    type45 += cost
    
    #full_cost += type45
    #if type03 <= 60.0:
    #  full_cost += type03
    #else:
    #  full_cost += 60.0

  
  return full_cost 

def get_simple_user_year_cost_under_coef(report_owner, year):
  year = int(year)

  full_cost = 0.0
  
  for act_type in range(act_type_num):
    full_cost += get_full_type_cost(report_owner, year, act_type)
      
  ys = get_user_yearstatistics(report_owner,year)      
  return calculate_coef_and_reason(report_owner, year)[0]*full_cost 
  
def get_simple_user_year_cost(report_owner, year):
  year = int(year)
  ys = get_user_yearstatistics(report_owner,year)      
  return get_simple_user_year_cost_under_coef(report_owner, year) #*get_coef_modifier(report_owner,year)+ys.additional_coef
  
def get_user_group_average(user, year):
  year = int(year)
  if is_lab_head(user):
    user_list = user.groups.all()[0].user_set.all()
    return get_group_average(user_list, year)
    
  return {
    'cost'        : 0.0,
    'explanation' : "",
  }
  
def get_group_average(user_list, year):
  year = int(year)
  full_other_cost = 0.0
  full_other_weight = 0
  
  other_average = 0.0
  verh = ""
  niz  = ""
  
  for u in user_list:
      if not is_laboratory(u):
         stavka = get_user_stavka(u) #w = get_user_weight(u)
         delta = get_simple_user_year_cost_under_coef(u, year)
         
         full_other_weight += stavka
         niz += str(stavka) + "+" # + u.first_name
         
         full_other_cost += delta*stavka
         verh += str(delta) + "*" + str(stavka) + "+"
      
  new_verh = verh[:-1]
  new_niz  = niz[:-1]

  new_explanation = ""
  if full_other_weight != 0.0:
    other_average = full_other_cost / full_other_weight
    new_explanation += "=(" + new_verh + ")/(" + new_niz + ")"
  else:
    new_explanation = ""
  
  return {
    'cost'        : other_average,
    'explanation' : new_explanation,
  }
  
def get_head_user_year_cost(report_owner, year):
  year = int(year)
 
  if is_inst_head(report_owner):
    user_list = User.objects.all()
  elif is_lab_head(report_owner):
    user_list = report_owner.groups.all()[0].user_set.all()
  
  other_average = get_group_average(user_list, year)['cost']
    
  ind_cost = get_simple_user_year_cost(report_owner, year)
  mixed_cost = 0.5*ind_cost + 0.75*other_average
  
  ys = get_user_yearstatistics(report_owner,year)
  
  if ys.calcasmaximum:
    if ind_cost > mixed_cost:
      return ind_cost

  return mixed_cost

# very ugly method!!
#def get_user_rank(user):
#  a = get_attribute(user)
#  
#  if a.rank == 'N':
#    return "net"
#  elif a.rank == 'Z':
#    return "zz"
#
# return "unknown"
