
# This Python file uses the following encoding: utf-8
import datetime

from prnd.legacy import forms
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseForbidden, HttpResponseNotAllowed
from prnd.register.djangohacks import login_required
from prnd.register.yearstat import get_user_yearstatistics, calculate_coef_and_reason
from django.contrib.auth import logout
from prnd.activity.models import *
from prnd.calculator.models import SelectedJournal
from prnd.activity.forms import *
from prnd.legacy.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from curses.ascii import isdigit
from django.contrib.auth.models import User
from prnd.activity.userreports import *
from prnd.activity.paths import *
from django.contrib.auth import authenticate
from prnd.calculator.send_mail import send_report_to_user

def get_detail_form(act_type, owner_id, modifier_id):
  if act_type == publication_type:
    return PublicationForm(owner_id, modifier_id)
  elif act_type == conference_type:
    return ConferenceForm(owner_id, modifier_id)
  elif act_type == patent_type:
    return PatentForm(owner_id, modifier_id)
  elif act_type == monograph_type:
    return MonographForm(owner_id, modifier_id)
  elif act_type == course_type:
    return CourseForm(owner_id, modifier_id)
  elif act_type == supervising_type:
    return SupervisingForm(owner_id, modifier_id)
  elif act_type == editing_type:
    return EditingForm(owner_id, modifier_id)
  elif act_type == editing_collegium_type:
    return EditingCollegiumForm(owner_id, modifier_id)
  elif act_type == orgwork_type:
    return OrgWorkForm(owner_id, modifier_id)
  elif act_type == opposing_type:
    return OpposingForm(owner_id, modifier_id)
  elif act_type == grant_type:
    return GrantForm(owner_id, modifier_id)
  elif act_type == award_type:
    return AwardForm(owner_id, modifier_id)
  
# whether a user with given id can see a given activity
def can_see_and_modify(act, user_id):
  return user_ge (user_id, act.user.id)
  
def parameters_needed_to_base(request, act_name=""):
  return {
    'request'      : request,
    'is_zavlab'     : is_zavlab(request.user),
    'is_admin'      : is_admin(request.user),
    'is_laboratory' : is_laboratory(request.user),
    'is_institute'  : is_institute(request.user),
    'new_action'    : False,
    'back_action'   : False,
    'delete_action' : False,
    'act_id'        : 0,
    'saved'         : False,
    'act_name'      : act_name,
    'wbreport'      : False,
    'username'      : request.user.username,
    'uid'           : request.user.id,
    'report_years'  : list(range(2005, datetime.date.today().year+1)),
  }
  
def NotAllowed(request):
  params = parameters_needed_to_base(request)
  params['comment'] = "У Вас нет прав для просмотра этой страницы."
  return render_to_response("general_comment.html", params)
  
def NotAllowedToModifyReport(request):
  params = parameters_needed_to_base(request)
  params['comment'] = "Вы не можете редактировать отчет за этот год."
  return render_to_response("general_comment.html", params)
  
@login_required
def activity_index(request, act_name):
  return HttpResponseRedirect("/prnd/" + act_name + "/"+str(request.user.id)+"/")
  
@login_required
def user_activity_index(request, act_name, userid):
  if not user_ge(request.user.id, userid):
    return NotAllowed(request)
    
  owner = get_object_or_404(User, pk=userid)

  try:
    act_type = name2type(act_name)
  except ValueError:
    raise Http404
  
  act_list = get_user_activity_list(owner, act_type)
  full_info_act_list = []
  for act in act_list:
    full_info_act_list.append({
      'id'        :    act.id,
      'html_str'  :    act2html(act_type, act),
      'cost'      :    get_activity_cost(act_type, act),
    })
    
  params = parameters_needed_to_base(request, act_name)
  params['new_action']           = True
  params['new_path']             = get_new_act_path(act_type, owner.id)
  params['full_info_act_list']   = full_info_act_list
  params['act_type_name']        = type2rusname1(act_type)
  params['act_type_name2']       = type2rusname2(act_type)
  params['name']                 = owner.last_name + " " + owner.first_name
  params['owner_id']             = owner.id
  params['owner_name']           = owner.last_name

  return render_to_response("acts/act_index.html", params )
  
@login_required
def main(request):
  return render_to_response('acts/mainpage.html', parameters_needed_to_base(request) )
  
@login_required
def personal_menu(request):
  return render_to_response('acts/personal_menu.html', parameters_needed_to_base(request) )
  

@login_required
def delete(request, act_name, userid, act_id):
  if not user_ge(request.user.id, userid):
    return NotAllowed(request)

  try:
    act_type = name2type(act_name)
  except ValueError:
    raise Http404

  act = get_activity_from_db(act_type, act_id)
  owner = get_object_or_404(User, pk=userid)
  
  if not can_see_and_modify(act, request.user.id):
    return NotAllowed(request)
    
  if not can_add_or_modify_activity(request.user.id, act.user.id, act.year):
    return NotAllowedToModifyReport(request)
    
  params = parameters_needed_to_base(request, act_name)
  params['back_action'] = True
  params['back_path']   = get_back_act_path(act_type, userid)
  params['owner_id']    = owner.id
  params['owner_name']  = owner.last_name
 

  if not request.POST: 
    params['act']      = act
    params['act_name'] = act_name
    params['name']     = act2html(act_type, act)
    return render_to_response('acts/delete.html', params )

  if "yes" == request.POST['post']:
    act.delete()
    params['already_deleted']=True
    return render_to_response('acts/delete.html', params )
  
  return HttpResponseRedirect("/prnd/"+get_back_act_path(act_type, userid))
  
@login_required
def logout_view(request):
  logout(request)
  return HttpResponseRedirect("/prnd/",)
  
@login_required
def modify(request, act_name, userid, act_id=0):
  try:
    act_type = name2type(act_name)
  except ValueError:
    raise Http404
  
  owner_id = int(userid)
  
  owner = get_object_or_404(User, pk=userid)
  
  if act_id != 0:
    cur_act = get_activity_from_db(act_type, act_id)
    if not user_ge(request.user.id, owner_id):
      return NotAllowed(request)
    
    if not can_add_or_modify_activity(request.user.id, owner_id, cur_act.year):
      return NotAllowedToModifyReport(request)
    
  form = get_detail_form(act_type, owner_id, request.user.id)
  params = parameters_needed_to_base(request, act_name)
  params['back_action'] = True
  params['back_path']   = get_back_act_path(act_type, userid)
  params['owner_id']    = owner_id
  params['owner_name']  = owner.last_name
     
  if act_id != 0:
    params['action']        = act_id
    params['delete_action'] = True
    params['delete_path']   = get_delete_act_path(act_type, userid, cur_act)
    params['act_name']      = act_name
    params['act_id']        = act_id
  else:
    params['action']        = "add"

  params['back_action'] = True
  params['saved'] = False
  
  if not request.method == 'POST':
    form_errors = {}
    if act_id == 0:
      form_data = {}
    else:
      cur_act = get_activity_from_db(name2type(act_name), act_id)
      form_data = cur_act.__dict__
  else:
    form_data = request.POST.copy()
    form_errors = form.get_validation_errors(form_data)
    
    if not form_errors:
      form.do_html2python(form_data)
      act = form.form2object(form_data, owner_id)
      if act_id == 0:
        act.save ()
        params['saved'] = True
        return HttpResponseRedirect("/prnd/" + get_back_act_path(act_type, userid))
      else:
        act.id = act_id
        act.save ()
        params['saved'] = True
     
  params['form']  = forms.FormWrapper(form, form_data, form_errors)
  params['new_action'] = True
  params['new_path']   = get_new_act_path(act_type, userid)

  return render_to_response(get_detail_file_name(act_type), params)

@login_required
def all_user_reports(request):
  """Рейтинги / список пользователей.

  Исторически страница использовалась:
  - администратором: видеть всех пользователей
  - завлабом: видеть пользователей своей группы (лаборатории)
  - обычным пользователем: видеть свою группу (если есть), иначе только себя
  """

  if is_admin(request.user):
    user_list = list(User.objects.all().order_by('last_name'))
  else:
    g = request.user.groups.first()
    if g:
      user_list = list(g.user_set.all().order_by('last_name'))
    else:
      user_list = [request.user]

  # Не показываем пользователей из служебной группы id=10 (если такая есть)
  user_list = [u for u in user_list if not u.groups.filter(id=10).exists()]

  user_list.sort(key=lambda u: (
    (u.groups.first().name if u.groups.first() else ""),
    (u.last_name or ""),
    (u.first_name or ""),
    u.username,
  ))

  params = parameters_needed_to_base(request)
  params['user_list'] = user_list
  return render_to_response('acts/all_user_reports.html', params)

  
@login_required
def cur_user_attestation(request):
  return HttpResponseRedirect("/prnd/"+get_user_attestation_path(request.user.id))
#  return user_attestation(request, request.user.id)

# very ugly method!!
def get_user_rank(user):
  a = get_attribute(user)
  if a.rank == 'Z':
    return "Z"
  return "unknown"

# attestation method
@login_required
def user_attestation(request, userid):
  if not user_ge(request.user.id, userid):
    return NotAllowed(request)
    
  user    = get_object_or_404(User, pk=userid)
  curuser = get_object_or_404(User, pk=request.user.id)
    
  params = parameters_needed_to_base(request)  
  form = AttestationForm()
  
  yfrom = 2005 #datetime.date.today().year-4
  yto   = datetime.date.today().year
        
  if not request.method == 'POST':
    form_errors = {}
    form_data   = {
      'yearfrom'  : yfrom,
      'yearto'    : yto,
      }
  else:
    form_data   = request.POST.copy()
    form_errors = form.get_validation_errors(form_data)
    
    if not form_errors:
      form.do_html2python(form_data)
      
      yearfrom = int(form_data['yearfrom'])
      yearto   = int(form_data['yearto'])
      
      year_list = list(range(yearfrom, yearto + 1))
      
      detailed_reports = ""
      for tempyear in year_list:
        ys = get_user_yearstatistics(user,tempyear)
      detailed_reports += "<br><b>" + str(tempyear) + ": </b>" + ys.detailed_report
      
      params['year_list'] = year_list
      params['yearfrom']  = yearfrom
      params['yearto']    = yearto
      params['realname']  = user.last_name + " " + user.first_name
      params['laboratory']= (user.groups.first().name if user.groups.first() else "")
      params['rank']      = get_user_rank(user) #RANK_CHOICES.has_key('N') #RANK_CHOICES.index(get_attribute(user).rank) #RANK_CHOICES[get_attribute(user).rank][1]
      params['report']    = detailed_reports
      
      report_owner = user
      
      typed_act_list = []
      for act_type in range(act_type_num):
        if act_type == opposing_type or act_type == editing_collegium_type:
          continue
        
        full_info_act_list = []
        for tempyear in year_list:
          act_list = get_user_activity_list_on_given_year(report_owner, act_type, tempyear)
          for act in act_list:
            full_info_act_list.append({
              'html_str'            : act2html(act_type, act),
            })
        
        typed_act_list.append({
          'full_info_act_list' : full_info_act_list,
          'act_type_name'      : type2name(act_type),
          'act_type_name1'     : type2rusname1(act_type),
          'act_type_name2'     : type2rusname2(act_type) + ". "
        })
      
      params['typed_act_list'] = typed_act_list
      return render_to_response("acts/attestation_report.html", params)
      

  params['form'] = forms.FormWrapper(form, form_data, form_errors)
  return render_to_response("acts/attestation_filter.html", params)
  
@login_required
def user_reports(request):
  return HttpResponseRedirect("/prnd/user_report/"+str(request.user.id))

@login_required
def user_report(request, userid):
  if not user_ge(request.user.id, userid):
    return NotAllowed(request)
    
  user    = get_object_or_404(User, pk=userid)
  curuser = get_object_or_404(User, pk=request.user.id)
  
  params = parameters_needed_to_base(request)
  
  year_reports = []
  for year in range(2005, datetime.date.today().year + 1):
    cost = get_user_year_cost(user, year)
    #coef = get_coef(user, year)
    year_reports.append({
      'year'              : year,
      'status'            : get_str_short_status_report(user, year),
      'cost'              : cost,
    })

  params['nickname']       = user.username
  params['realname']       = user.last_name + " " + user.first_name
  params['year_reports']   = year_reports
  params['userid']         = userid
  params['owner_id']       = userid
  params['owner_name']     = user.last_name  

  return render_to_response("acts/user_reports.html", params)

@login_required
def cur_user_year_report(request, year):
  year = int(year)
  return HttpResponseRedirect("/prnd/"+get_user_report_path(request.user.id, year))  

@login_required
def wbyear_reports(request, userid, year):
  return year_reports(request, userid, year, True)
    
@login_required
def year_reports(request, userid, year, wbreport=False):
  params = parameters_needed_to_base(request)
  params['wbreport'] = wbreport
  year = int(year)
  report_owner_id = int(userid)
  
  if not user_ge(request.user.id, report_owner_id):
    return NotAllowed(request)
      
  report_owner  = get_object_or_404(User, pk=report_owner_id)
  curuser       = get_object_or_404(User, pk=request.user.id)
  ys            = get_user_yearstatistics(report_owner,year)
  
  old_status = int(ys.status)

  typed_act_list = []
  full_cost = 0.0
  full_num = 0
  for act_type in range(act_type_num):
    act_list = get_user_activity_list_on_given_year(report_owner, act_type, year)
    full_info_act_list = []
    full_cost += get_full_type_cost(report_owner, year, act_type)
    for act in act_list:
      full_num += 1
    
      full_info_act_list.append({
        'act_path'            : get_act_path(act_type, userid, act),
        'html_str'            : act2html(act_type, act),
        'cost'                : get_activity_cost(act_type, act)
      })
        
    typed_act_list.append({
      'full_info_act_list' : full_info_act_list,
      'act_type_name'      : type2name(act_type),
      'act_type_name1'     : type2rusname1(act_type),
      'act_type_name2'     : type2rusname2(act_type),
      'add_path'           : "/prnd/" + get_new_act_path(act_type, userid),
      'total'              : get_full_type_cost(report_owner, year, act_type),
    })

  report_list = []
  
  user_list = []
  if is_laboratory(request.user):
    not_filtered_user_list = ((request.user.groups.first().user_set.all().order_by('last_name')) if request.user.groups.first() else User.objects.none())
    for u in not_filtered_user_list:
      if not is_laboratory(u) and not is_institute(u):
        user_list.append(u)      
  elif is_institute(request.user):
    not_filtered_user_list = User.objects.all();
    for u in not_filtered_user_list:
      if is_laboratory(u):
        user_list.append(u)      
  else:
    user_list = []
    
  user_report_list = [] # all (laboratory) user reports for the corresponding year

  for user in user_list:
    user_report_list.append({
      'name'            : user.last_name + " " + user.first_name,
      'userid'          : user.id,
      'detailed_report' : get_user_detailed_report (user, year),
      })
      
  params['year']           = year
  params['nickname']       = report_owner.username
  name = report_owner.last_name + " " + report_owner.first_name
  params['realname']       = name
  params['user_profile_path'] = "/prnd/" + get_user_profile_path(report_owner.id)
  params['typed_act_list'] = typed_act_list
  params['user_report_list'] = user_report_list
  #params['lab_list'] = lab_list
  params['full_cost']      = full_cost
  params['empty']          = full_num == 0
  params['userid']         = report_owner_id
    
  form = UserReportForm(curuser)
     
  if not request.method == 'POST':
    form_errors = {}
    form_data = ys.__dict__
  else:
    form_data   = request.POST.copy()
    form_errors = form.get_validation_errors(form_data)
    
    if not form_errors:
      form.do_html2python(form_data)
      form.save(ys, form_data)
      ys.save ()
      params['saved'] = True
      
      if int(ys.status) != int(old_status):
        send_report_to_user(report_owner, report_owner, year)
  
  params['form']           = forms.FormWrapper(form, form_data, form_errors)
  # status params
  params['calculated_cost'] = get_user_year_cost(report_owner, year)
  can_modify = is_admin(curuser) or (int(ys.status) < int(get_maximal_report_status_choice(curuser)))
  can_modify = can_modify and not wbreport
  params['can_modify'] = can_modify
  params['can_modify_status'] = can_modify
  params['status'] = get_str_status_report(report_owner, year)
  params['can_modify_reason'] = can_modify and ( is_zavlab(curuser) or is_admin(curuser) )
  params['detailed_report'] = (ys.detailed_report or "").replace('\n','<br>')
  params['reason'] = (ys.reason or "").replace('\n', '<br>')
  params['can_modify_detailed_report'] = can_modify
  params['detailed_report'] = (ys.detailed_report or "").replace('\n', '<br>')
  params['can_modify_coef'] = can_modify and is_admin(curuser)
  params['coef_modifier'] = ys.coef_modifier
  params['can_modify_additional_coef'] = can_modify and is_admin(curuser)
  params['additional_coef'] = ys.additional_coef
  params['can_see_calc_as_maximum_flag'] = is_admin(curuser) and is_lab_head(report_owner)
  params['can_modify_calc_as_maximum_flag'] = can_modify and is_admin(curuser)
  if ys.calcasmaximum == True:
    params['calcasmaximum'] = 'как максимум'
  else:
    params['calcasmaximum'] = 'как 75% среднего ПРНД сотрудников подразделения + 50% индивидуального ПРНД'

  coef_and_reason = calculate_coef_and_reason(report_owner, year)
  params['def_coef']    = coef_and_reason[0] 
  params['def_reason']  = coef_and_reason[1]
  params['owner_id']    = report_owner.id
  params['owner_name']  = report_owner.last_name
  params['can_see_group_average'] = is_lab_head(report_owner)
  if is_lab_head(report_owner):
    params['group_average'] = get_user_group_average(report_owner, year)['cost']
    params['group_average_explanation'] = get_user_group_average(report_owner, year)['explanation']
  
  return render_to_response("acts/single_user_statistics.html", params )
 
@login_required
def laboratory_act_list(request, userid, year):
  #if not is_institute(request.user):
  #    return NotAllowed(request)

  params = parameters_needed_to_base(request)
  year = int(year)
  params['year'] = year
  user_lab  = get_object_or_404(User, pk=userid)
  params['name'] = user_lab.last_name + " " + user_lab.first_name
  #params['lab_user_id'] = user_lab.id
  
  #creating laboratory lists
  lab_list = []
  for act_type in range(act_type_num):
    lab = user_lab.groups.first()

    if not lab:

      break
    act_lab_list = []
    for u in lab.user_set.all():
      user_act_list = get_user_activity_list(u, act_type)
      for act in user_act_list:
        if int(act.year) == int(year):
          name = act2html( act_type, act )
          act_lab_list.append({
            'act'      : name,
            'username' : u.last_name + " " + u.first_name,
          })
    
    lab_list.append({
      'act_name' : type2rusname2(act_type),
      'act_list' : act_lab_list,
    })
  
  params['lab_list'] = lab_list
  
  return render_to_response("acts/laboratory_act_list.html", params )

@login_required
def all_year_acts(request, act_name, year):
  if not is_institute(request.user):
    return NotAllowed(request)
    
  try:
    act_type = name2type(act_name)
  except ValueError:
    raise Http404
  year = int ( year )    

  params = parameters_needed_to_base(request)
  params['year'] = year
  
  #creating laboratory lists
  not_filtered_user_list = list(User.objects.all().order_by('last_name'))
  not_filtered_user_list.sort(key=lambda u: (u.groups.first().name if u.groups.first() else ""))
  
  full_act_list = []
  for user in not_filtered_user_list:
    act_list = get_user_activity_list_on_given_year(user, act_type, year)
    for act in act_list:
      full_act_list.append({
        'username' : user.last_name + " " + user.first_name,
        'labname'  : (user.groups.first().name if user.groups.first() else ""),
        'actname'  : act2html (act_type, act),
      })
  
  params['act_list'] = full_act_list
  params['act_type_name'] = type2rusname1(act_type)
  
  return render_to_response("acts/all_year_acts.html", params )
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.template import TemplateDoesNotExist


@login_required
def full_statistics(request):
    try:
        return render(request, "acts/full_statistics.html", {})
    except TemplateDoesNotExist:
        return HttpResponse(
            "full_statistics: template acts/full_statistics.html not found",
            content_type="text/plain",
        )

