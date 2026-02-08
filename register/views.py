# This Python file uses the following encoding: utf-8
import datetime
import random
import hashlib
from random import choice
from prnd.legacy import forms
from prnd.legacy.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from prnd.register.forms import RegistrationForm, ProfileForm, PasswordForm, ForgotForm
from prnd.register.models import UserProfile
from prnd.activity.views import parameters_needed_to_base, NotAllowed
from prnd.activity.userreports import user_ge, is_admin, is_zavlab
from prnd.register.djangohacks import login_required
from prnd.register.yearstat import get_user_yearstatistics
from django.contrib.auth.models import User
from prnd.activity.userreports import *
from prnd.calculator.attributes import get_attribute
from prnd.calculator.send_mail import site, mail


@csrf_exempt
def login_view(request):
    """Legacy login view (CSRF-exempt for compatibility with old templates)."""
    params = {}
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Respect ?next=
            next_url = request.GET.get("next") or request.POST.get("next")
            return HttpResponseRedirect(next_url or "/prnd/")
        params["error"] = "Неверный логин или пароль."

    # GET or failed POST
    return render_to_response("registration/login.html", params)

def send_mail_to_user(user):
      # Build the activation key for their account
      salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
      activation_key = hashlib.sha1((salt + user.username).encode('utf-8')).hexdigest()
      key_expires = datetime.datetime.today() + datetime.timedelta(2)
      
      # Create and save their profile
      new_profile = UserProfile(user=user,
          activation_key=activation_key,
          key_expires=key_expires)
      new_profile.save()

       # Send an email with the confirmation link 
      email_subject = 'zapros na vosstanovlenie parolya'
      email_body = "Уважаемый %s,\n\nОт Вашего имени был получен запрос на\
 восстановление пароля на сайте %s. \n\n Для восстановления пароля Вам следует в\
 течение 48 часов посетить страницу\n\n %s/change/%s\n\n" % (
            user.last_name + " " + user.first_name,
            site, site,
            new_profile.activation_key)
      email_body += "Zdravstvuite!\n\nOt Vashego imeni byl poluchen zapros na \
vosstanovlenie parolja na sajte %s. \n\n Dlja vosstanovlenija parolja Vam sleduet v \
techenie 48 chasov posetit' stranitsu\n\n %s/change/%s\n\n" % (
            site, site,
            new_profile.activation_key)
      send_mail(email_subject,
          email_body,
          mail,
          [user.email])
      return

def forgot(request):
  if request.user.is_authenticated:
    return render_to_response('registration/already.html',)

  form = ForgotForm()
  if request.method == 'POST':
    data = request.POST.copy()
    errors = form.get_validation_errors(data)
    if not errors:
      form.do_html2python(data)
      for user in form.save(data):
        send_mail_to_user(user)

      return render_to_response("registration/recalled.html")
  else:
    errors, data = {}, {}
 
  return render_to_response("registration/forgot.html",{
      'form' : forms.FormWrapper(form, data, errors),
      }) 

@login_required
def change(request):
    form = PasswordForm(request.user.id, True)
    
    changed = False

    if request.method == 'POST':
        data = request.POST.copy()
        errors = form.get_validation_errors(data)
        if not errors:
          form.do_html2python(data)
          request.user = form.save(data)
          request.user.save()
          changed = True
    else:
        errors, data = {}, {}

    params = parameters_needed_to_base(request, False)
    params['form']    = forms.FormWrapper(form, data, errors)
    params['changed'] = changed
    return render_to_response("registration/change.html", params)

def delete_profile(request, id=0):
  if id == 0:
    id = request.user.id
  if not user_ge(request.user.id,id) or int(request.user.id) == int(id):
    return NotAllowed (request)
  
  user = get_object_or_404(User, pk=id)

  if request.user == user:
    return NotAllowed (request)

  params = parameters_needed_to_base(request)
  
  params['name'] = user.last_name + " " + user.first_name

  if not request.POST:
    return render_to_response('registration/user_delete.html', params )
    
  if "yes" == request.POST['post']:
    user.delete()
    params['already_deleted']=True
    return render_to_response('registration/user_delete.html', params )

  return HttpResponseRedirect("/prnd/profile/" + str(id))
  
@login_required
def profile(request, id=0):
  if id == 0:
    id = request.user.id
  return HttpResponseRedirect("/prnd/profile/" + str(id))
  
def modify_profile(request, id):
    user = get_object_or_404(User, pk=id)
    
    form = ProfileForm(user)

    ys = get_user_yearstatistics(user, datetime.date.today().year)

    saved = False
    zavlab = is_zavlab(request.user)
    is_boss = is_admin(request.user) or zavlab
    if request.method == 'POST':
        data = request.POST.copy()
        errors = form.get_validation_errors(data)
        if not errors:
          form.do_html2python(data)
          
          # assign nonshown fields
          a = get_attribute(user)
          if not is_boss:
            data["is_headlab"] = a.is_headlab

          if a.is_zavlab:
            data["is_zavlab"] = a.is_zavlab

          if request.user == user:
            data["is_zavlab"] = a.is_zavlab
            data["is_admin"]  = a.is_admin

          # anti-EA fix --- zavlab cannot change is_zavlab and group at
          # the same time
            g = request.user.groups.first()
            if g:
              data["groups"] = g.id
          if a.is_zavlab and zavlab:
            g = request.user.groups.first()
            if g:
              data["groups"] = g.id

          user = form.save(data, user.id)
          user.save()

          a = get_attribute(user)
          if is_boss and a.is_zavlab:
            g = user.groups.first()
            ulist = g.user_set.all() if g else []
            for u in ulist:
              if u == user:
                continue
              ua = u.attribute
              ua.is_zavlab = False
              ua.save()

          if a.is_admin:
            ulist = User.objects.all()
            for u in ulist:
              if u == user:
                continue
              ua = u.attribute
              ua.is_admin = False
              ua.save()

          form = ProfileForm(user)
          saved = True
    else:
        errors = {}
        data   = ys.__dict__
        # note that ys has status also
        a      = get_attribute(user)
        data.update(a.__dict__)
        data.update(user.__dict__)
        data.update([('groups', s.id) for s in user.groups.all()])

    params = parameters_needed_to_base(request, False)
    params['form']    = forms.FormWrapper(form, data, errors)
    params['modify']  = 1 
    params['saved']   = saved
    params['group'] = user.groups.first()
    params['change_passwd'] = user == request.user 
    params['owner_id']    = user.id
    params['owner_name']  = user.last_name
    params['zavlab_non_modify'] = a.is_zavlab

    if not user_ge(request.user.id,id):
      return NotAllowed (request)

    return render_to_response("registration/register.html", params)


def register(request):
    if request.user.is_authenticated: 
    # They already have an account; don?t let them register again 
      return render_to_response('registration/already.html', ) 

    form = RegistrationForm()

    if request.method == 'POST':
        data = request.POST.copy()
        errors = form.get_validation_errors(data)
        if not errors:
          form.do_html2python(data)
          new_user = form.save(data)

          # Build the activation key for their account
          salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
          activation_key = hashlib.sha1((salt + new_user.username).encode('utf-8')).hexdigest()
          key_expires = datetime.datetime.today() + datetime.timedelta(2)
      
          # Create and save their profile
          new_profile = UserProfile(user=new_user,
              activation_key=activation_key,
              key_expires=key_expires)
          new_profile.save()

          # Send an email with the confirmation link 
          email_subject = 'aktivatsiya uchetnoi zapisi'
          email_body = "Уважаемый %s,\n\nОт Вашего имени был получен запрос на \
регистрацию на сайте  %s \n\n Для активации Вашей учетной записи, \
Вам следует в течение 48 часов посетить страницу\n\n %s/confirm/%s\n\n" % (
            new_user.last_name + " " + new_user.first_name,
            site,site,
            new_profile.activation_key)
          email_body += "Zdravstvuite!\n\nOt Vashego imeni byl poluchen \
zapros na registratsiju na sajte  %s \n\n Dlja aktivatsii Vashej uchetnoj \
zapisi, Vam sleduet v techenie 48 chasov posetit' \
stranitsu\n\n %s/confirm/%s\n\n" % (
            site,site,
            new_profile.activation_key)

          send_mail(email_subject,
              email_body,
              mail,
              [new_user.email])
          return render_to_response("registration/created.html",) 
    else:
        data, errors = {}, {}

    return render_to_response("registration/register.html", {
        'form' : forms.FormWrapper(form, data, errors),
        'unlog': 1
    })
    
def confirm(request, activation_key):
    if request.user.is_authenticated:
        return render_to_response('registration/already.html',)
    user_profile = get_object_or_404(UserProfile,
                                     activation_key=activation_key)
    if user_profile.key_expires < datetime.datetime.today():
        return render_to_response('registration/confirm.html', {'expired': True})
    user_account = user_profile.user
    user_account.is_active = True
    user_account.save()
    return render_to_response('registration/confirm.html', {'success': True})

def change_forgot(request, activation_key):
    if request.user.is_authenticated:
        return render_to_response('registration/already.html',)

    user_profile = get_object_or_404(UserProfile, activation_key=activation_key)
    if user_profile.key_expires < datetime.datetime.today():
        return render_to_response('registration/confirm.html', {'expired': True})
    form = PasswordForm(user_profile.user.id, False)
        
    if request.method == 'POST':
        data = request.POST.copy()
        errors = form.get_validation_errors(data)
        if not errors:
          form.do_html2python(data)
          user_profile.user = form.save(data)
          user_profile.user.is_active = True
          user_profile.user.save()
          user_profile.delete()
          return render_to_response("empty_comment.html",{
            'comment': "Поздравляем! Вы успешно сменили свой пароль<br>\
            <a href=\"/prnd/\">Начать работу.</a>",
            })
    else:
        errors, data = {}, {}

    return render_to_response("registration/change_forgot.html", {
        'form' : forms.FormWrapper(form, data, errors),
        'no_old': True,
        'username':user_profile.user.username,
    })

