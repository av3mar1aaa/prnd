# This Python file uses the following encoding: utf-8
import re
from django.contrib.auth.decorators import user_passes_test 
from prnd.calculator.models import * 
from django.http import HttpResponseRedirect, Http404
from prnd.legacy.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from prnd.calculator.forms import * 
from prnd.activity.forms import Activity,Editing,Monograph
from prnd.activity.acttypes import *
from prnd.activity.paths import *
from prnd.activity.userreports import *
from prnd.activity.views import parameters_needed_to_base
from prnd.legacy import forms
from prnd.activity.userreports import is_admin
from prnd.activity.views import NotAllowed
from prnd.register.djangohacks import login_required

def get_journal_list_path():
  return "sjournal/"
  
def get_journal_path(journal):
  return "sjournal/" + str(journal.id) + "/"
  
def get_journal_add_path():
  return "sjournal/add/"
  
def get_journal_delete_path(journal):
  return "sjournal/" + str(journal.id) + "/delete/"

@login_required
def add_sjournals_list(request, list_name):
  if not is_admin(request.user):
    return NotAllowed(request)

  if list_name != 'A' and list_name != 'B' and list_name != 'P':
    raise Http404
    
  form = addSelectedJournalList()
  if request.method == 'POST':
    data = request.POST.copy()
    errors = form.get_validation_errors(data)
  
    if not errors:
      form.do_html2python(data)
      new_list = form.getList(data)
      for j in new_list:
        if not j.isspace():
          fn = j
          SelectedJournal.objects.create(fullname=fn,type=list_name)
      return HttpResponseRedirect("/prnd/" + get_journal_list_path())
  else:
    errors = {}
    data = {}
  
  params = parameters_needed_to_base(request)
  params['form']        = forms.FormWrapper(form, data, errors)
  params['back_action'] = True
  params['act_name']    = 'sjournal'
  params['list_name']   = list_name
  params['back_action'] = True
  params['back_path'] = get_journal_list_path()

  return render_to_response("statistics/add_sjournal_list.html", params )

@login_required
def delete(request, id):
  if not is_admin(request.user):
    return NotAllowed (request)
    
  params = parameters_needed_to_base(request)

  journal = get_object_or_404(SelectedJournal, pk=id)
  
  list_of_dependable_objects = []
  total_num = 0
  for act_type in [publication_type, monograph_type]:
    act_list = get_full_activity_list(act_type)
    for act in act_list:
      if int(act.journal_id) == int(id):
        total_num += 1
        list_of_dependable_objects.append({
          'act_type'      : act_type,
          'act_type_name' : type2name(act_type),
          'act'           : act,
          'cost'          : get_activity_cost(act_type, act),
          'html_str'      : act2html(act_type, act),
	  'path'          : "/prnd/" + get_modify_act_path(act_type, act.user.id, act),
        })
        
  params['name'] = journal.fullname
  params['list'] = list_of_dependable_objects
  params['there_are_dependable_objects'] = total_num > 0
  params['back_action'] = True
  params['back_path'] = get_journal_list_path()
  
  if not request.POST: 
    return render_to_response('statistics/sjournal_delete.html', params )
    
  if "yes" == request.POST['post']:
    for obj in list_of_dependable_objects:
      obj['act'].journal_id = 0
      obj['act'].journal = journal.fullname
      obj['act'].save()
    journal.delete()
    params['already_deleted']=True
    return render_to_response('statistics/sjournal_delete.html', params )

  return HttpResponseRedirect("/prnd/" + get_journal_list_path())

@login_required
def sjournal_list(request):
  if not is_admin(request.user):
    return NotAllowed (request)
    
  params = parameters_needed_to_base(request)
  # ot etogo dublirovaniya horosho bi izbavit'sya!
  listA = SelectedJournal.objects.filter(type='A').order_by('fullname') 
  listB = SelectedJournal.objects.filter(type='B').order_by('fullname')
  listP = SelectedJournal.objects.filter(type='P').order_by('fullname')
  params['listA']      = listA
  params['listB']      = listB
  params['listP']      = listP
  params['new_action'] = True
  params['new_path']   = get_journal_add_path()
  params['act_name']   = 'sjournal'
  params['is_admin']   = True

  return render_to_response('statistics/sjournal_list.html', params )

@login_required
def sjournal_modify(request, id=0):
  if not is_admin(request.user):
    return NotAllowed (request)

  params = parameters_needed_to_base(request)
  params['back_action'] = True
  params['back_path']   = get_journal_list_path()

  if id != 0:
    j = get_object_or_404(SelectedJournal, pk=id)
    params['delete_action'] = True
    params['delete_path']   = get_journal_delete_path(j)
  else:
    params['delete_action'] = False

  form = SelectedJournalForm()
  if request.method == 'POST':
    data = request.POST.copy()
    errors = form.get_validation_errors(data)
  
    if not errors:
      form.do_html2python(data)
      new_j = form.form2object(data)
      if id != 0:
        new_j.id = id
      new_j.save()
      params['saved'] = True
  else:
    errors = {}
    data = {}
    if id != 0:
      data.update(j.__dict__)

  params['form']     = forms.FormWrapper(form, data, errors),
  params['act_name'] = get_journal_list_path ()
  params['act_id']   = id
  
  return render_to_response("statistics/sjournal_detail.html", params )

@login_required
def new_sjournal_modify(request, id=0):
  if not is_admin(request.user):
    return NotAllowed (request)

  if id != 0:
    journal = get_object_or_404(SelectedJournal, pk=id)
    
  form = SelectedJournalForm()

  params = parameters_needed_to_base(request)
  params['back_action'] = True
  params['back_path']   = get_journal_list_path()
  
  if id != 0:
    params['action']        = id
    params['delete_action'] = True
    params['delete_path']   = get_journal_delete_path(journal)
    #params['act_name']      = act_name
    params['act_id']        = id
  else:
    params['action']        = "add"

  params['back_action'] = True
  params['saved'] = False
  
  if not request.method == 'POST':
    form_errors = {}
    if id == 0:
      form_data = {}
    else:
      form_data = journal.__dict__
  else:
    form_data = request.POST.copy()
    form_errors = form.get_validation_errors(form_data)
    
    if not form_errors:
      form.do_html2python(form_data)
      journal = form.form2object(form_data)
      if id == 0:
        journal.save ()
        params['saved'] = True
        return HttpResponseRedirect("/prnd/" + get_journal_list_path())
      else:
        journal.id = id
        journal.save ()
        params['saved'] = True
     
  params['form']  = forms.FormWrapper(form, form_data, form_errors)
  params['new_action'] = True
  params['new_path'] = get_journal_add_path()

  return render_to_response("statistics/sjournal_detail.html", params)
