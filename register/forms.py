# This Python file uses the following encoding: utf-8
import random, re, datetime

from prnd.legacy import validators
from prnd.legacy import forms
from django.contrib.auth.models import User, Group, AnonymousUser 
from prnd.calculator.models import Attribute
from prnd.calculator.attributes import get_attribute
from prnd.register.djangohacks import IntegerField

def isValidYear(field_data, all_data):
  next_year = datetime.date.today().year 
  if int(field_data)<1900 or int(field_data) > next_year:
    raise validators.ValidationError("Введите год от 1900 до %s" % next_year)
  return

def isValidDegree(field_data, all_data):
  if field_data == 'N' and all_data['phd_year'] != "":
     raise validators.ValidationError("Укажите степень, которую Вы получили в %s году" % all_data['phd_year'])
    
def isValidStatus(field_data, all_data):
  if field_data == 'S':
    if all_data['phd_year'] != '' or all_data['degree'] != 'N':
      raise validators.ValidationError("Вы уже получили степень в %s году" % all_data['phd_year'])
    if all_data['diplom_year'] == '':
      raise validators.ValidationError("Вы не можете быть аспирантом, не имея высшего образования")
  return 

class isValidRank(object):
  def __init__(self, user):
    self.user = user
    
  def __call__(self, field_data, all_data):
    if all_data['status'] != 'N' and  field_data != 'N':
      raise validators.ValidationError("Вы не можете иметь должность, не являясь сотрудником")
    
    if field_data == 'Z' or  field_data == 'D':
      group_id = all_data['groups']
      if field_data == 'D':
        error = "У института уже есть директор"
      if group_id == None:
        return
      group = Group.objects.get(id=group_id)  
      for r in Attribute.objects.all():
        if r.user == self.user:
          continue
        if r.rank == 'Z' and field_data == 'Z':
          for g in r.user.groups.all():
            if group == g:
              error = "У лаборатории %s уже есть заведующий" % g.name
              raise validators.ValidationError(error)
        elif r.rank == 'D' and field_data == 'D':
          raise validators.ValidationError(error)
    return

class isValidHeadlab(object):
  def __init__(self, user):
    self.user = user
    
  def __call__(self,field_data, all_data):
    if all_data['status'] != 'N' and  field_data:
       raise validators.ValidationError("нельзя быть главой подразделения за лабораторию, не являясь сотрудником")
    if not field_data:
      return
    group_id = all_data['groups']
    if group_id == None:
      return
    group = Group.objects.get(id=group_id)  
    for r in Attribute.objects.all():
      if r.user == self.user:
        continue
      if r.is_headlab:
        for g in r.user.groups.all():
          if group == g:
            raise validators.ValidationError('У подразделения %s уже есть глава' % g.name)
    return

    
class isValidZavlab(object):
  def __init__(self, user):
    self.user = user
    
  def __call__(self,field_data, all_data):
    if all_data['status'] != 'N' and  field_data != 'N':
       raise validators.ValidationError("нельзя быть ответственным за лабораторию, не являясь сотрудником")
    if not field_data:
      return
    group_id = all_data['groups']
    if group_id == None:
      return
    if self.user.attribute.is_zavlab:
      return
    group = Group.objects.get(id=group_id)  
    for r in Attribute.objects.all():
      if r.user == self.user:
        continue
      if r.is_zavlab:
        for g in r.user.groups.all():
          if group == g:
            raise validators.ValidationError('У лаборатории %s уже есть ответственный' % g.name)
    return

def update_user(new_data, u):
    g = Group.objects.get(pk=int(new_data['groups'])) 
    u.groups.clear()
    u.groups.add(g)
    u.last_name= new_data['last_name']
    u.first_name= new_data['first_name']
    
    a = Attribute(rate=new_data['rate'],
        rank = new_data['rank'],
        status = new_data['status'],
        title = new_data['title'],
        phd_year = new_data['phd_year'],
        birth_year = new_data['birth_year'],
        diplom_year = new_data['diplom_year'],
        degree = new_data['degree'],
        user = u,
        email_verbose = new_data['email_verbose'],
        )
    if 'is_headlab' in new_data and new_data['is_headlab']:
      a.is_headlab = new_data['is_headlab']
    if 'is_zavlab' in new_data and new_data['is_zavlab']:
      a.is_zavlab= new_data['is_zavlab']
    if 'is_admin' in new_data and new_data['is_admin']:
      a.is_admin = new_data['is_admin']
    a.save()
    return u

    
class RegistrationForm(forms.Manipulator):
  def __init__(self):
    user = AnonymousUser()
    self.fields = (
    forms.TextField(field_name='username',
      length=30, maxlength=30,
      is_required=True, validator_list=[validators.isAlphaNumeric,
      self.isValidUsername]
      ),
    forms.TextField(field_name='last_name',
      length=30, maxlength=30,
      is_required=True
      ),
     forms.TextField(field_name='first_name',
      length=30, maxlength=30,
      is_required=True
      ),
    forms.EmailField(field_name='email',
      length=30,
      maxlength=30,
      is_required=True),
    forms.SelectField(field_name='groups',
      choices=[(s.id, s.name) for s in Group.objects.all()]
      ),
    IntegerField(field_name='diplom_year',
    length=4, maxlength=4,
    validator_list=[isValidYear]
    ),
    IntegerField(field_name='birth_year',
    length=4, maxlength=4, is_required=True,
    validator_list=[isValidYear]
    ),
    forms.SelectField(field_name='degree',
        choices=[s for s in Attribute.DEGREE_CHOICES],
        validator_list=[isValidDegree]
        ),
    IntegerField(field_name='phd_year',
    length=4, maxlength=4,
    validator_list=[isValidYear, validators.RequiredIfOtherFieldDoesNotEqual('degree', 'N',"Введите год, в котором Вы получили степень")]
    ),
    forms.SelectField(field_name='status',
        choices=[s for s in Attribute.STATUS_CHOICES],
        validator_list=[isValidStatus]
        ),
    forms.SelectField(field_name='rank',
      choices=[s for s in Attribute.RANK_CHOICES],
      validator_list=[isValidRank(user)],
      ),
    forms.SelectField(field_name='title',
      choices=[s for s in Attribute.TITLE_CHOICES],
      ),
    forms.SelectField(field_name='rate',
        is_required=True,
        choices=[s for s in Attribute.rate_choices ], 
      ),
    forms.CheckboxField(field_name='email_verbose',
        checked_by_default=True,
        ),
    forms.PasswordField(field_name='password1',
      length=30,
      maxlength=60,
      is_required=True),
    forms.PasswordField(field_name='password2',
      length=30, maxlength=60,
      is_required=True,
      validator_list=[validators.AlwaysMatchesOtherField('password1', 'Пароли не совпадают.')]),
    )
    
  def isValidUsername(self, field_data, all_data):
    try:
      User.objects.get(username=field_data)
    except User.DoesNotExist:
      return  
    raise validators.ValidationError('Учетная запись с именем "%s" уже существует.' % field_data)
 

  def save(self, new_data): 
    u = User.objects.create_user(new_data['username'],
        new_data['email'],
        new_data['password1'],)
    u = update_user(new_data, u)
    u.is_active = False
    u.save()
    return u

class ProfileForm(forms.Manipulator):
  def __init__(self, user):
    if user.attribute.is_zavlab:
      groups = [(s.id, s.name) for s in user.groups.all()] 
    else:
      groups = [(s.id, s.name) for s in Group.objects.all()]
    self.fields = (
    forms.TextField(field_name='last_name',
      length=30, maxlength=30,
      is_required=True
      ),
    forms.TextField(field_name='first_name',
      length=30, maxlength=30,
      is_required=True
      ),
    forms.EmailField(field_name='email',
      length=30,
      maxlength=30,
      is_required=True),
    forms.SelectField(field_name='groups',
      choices=groups
      ),
    IntegerField(field_name='diplom_year',
      length=4, maxlength=4,
      validator_list=[isValidYear]
    ),
    IntegerField(field_name='birth_year',
      length=4, maxlength=4, is_required=True,
      validator_list=[isValidYear]
    ),
    forms.SelectField(field_name='degree',
        choices=[s for s in Attribute.DEGREE_CHOICES],
        validator_list=[isValidDegree]
        ),
    IntegerField(field_name='phd_year',
    length=4, maxlength=4,
    validator_list=[isValidYear, validators.RequiredIfOtherFieldDoesNotEqual('degree', 'N', "Введите год, в котором Вы получили степень")]
    ),
    forms.SelectField(field_name='status',
        choices=[s for s in Attribute.STATUS_CHOICES],
        validator_list=[isValidStatus]
        ),
    forms.SelectField(field_name='rank',
      choices=[s for s in Attribute.RANK_CHOICES],
      validator_list=[isValidRank(user)],
      ),
    forms.SelectField(field_name='title',
      choices=[s for s in Attribute.TITLE_CHOICES],
      ),
    forms.SelectField(field_name='rate',
        is_required=True,
        choices=[s for s in Attribute.rate_choices ], 
      ),
    forms.CheckboxField(field_name='email_verbose',
        ),
    forms.CheckboxField(field_name='is_zavlab',
      ),
    forms.CheckboxField(field_name='is_admin',
      ),
    forms.CheckboxField(field_name='is_headlab',
        validator_list=[isValidHeadlab(user)],
      ),
    )
    
  def save(self, new_data, userid):
    u = User.objects.get(id=userid)
    u.email = new_data['email']
    u = update_user(new_data, u)
    u.id = userid
    u.save()
    return u

class PasswordForm(forms.Manipulator):
  def __init__(self, userid, old_required):
    self.fields = (
    forms.PasswordField(field_name='old_password',
      length=30,
      maxlength=60,
      is_required=old_required,
      validator_list=[self.isValidOldPassword]
      ),
    forms.PasswordField(field_name='password1',
      length=30,
      maxlength=60,
      is_required=True),
    forms.PasswordField(field_name='password2',
      length=30, maxlength=60,
      is_required=True,
      validator_list=[validators.AlwaysMatchesOtherField('password1', 'Пароли не совпадают.')]),
    forms.IntegerField(field_name='userid', member_name = userid)
    )
    
  def isValidOldPassword(self, field_data, all_data):
    userid = self.__getitem__('userid').get_member_name()
    u = User.objects.get(id=userid)
    if not u.check_password(field_data):
      raise validators.ValidationError('Введите Ваш текущий пароль.')
    return  
    
  def save(self, new_data):
    userid = self.__getitem__('userid').get_member_name()
    u = User.objects.get(id=userid)
    u.set_password(new_data['password1'])
    u.save()
    return u
  
class ForgotForm(forms.Manipulator):
  def __init__(self):
    self.fields = (
    forms.TextField(field_name='username',
      length=30, maxlength=30,
      validator_list=[validators.isAlphaNumeric, validators.RequiredIfOtherFieldNotGiven('email'),self.isValidUsername]
      ),
    forms.EmailField(field_name='email',
      length=30,
      maxlength=30,
      validator_list=[validators.RequiredIfOtherFieldNotGiven('username'), self.isValidEmail]),
    )

  def isValidUsername(self, field_data, all_data):
    try:
      User.objects.get(username=field_data)
    except User.DoesNotExist:
      raise validators.ValidationError('Учетной записи с таким именем не существует.')
    if all_data['username'] == "":
      raise validators.ValidationError('Вы уже ввели адрес электронной почты.')
    return
  
  def isValidEmail(self, field_data, all_data):
    try:
      User.objects.filter(email=field_data)
    except User.DoesNotExist:
      raise validators.ValidationError('Учетной записи с таким электронным адресом не существует.')
    if all_data['email'] == "":
      raise validators.ValidationError('Вы уже ввели имя учетной записи.')
    return 
  

  def save(self, new_data):
    list = []
    if new_data['username'] != '':
      u = User.objects.get(username=new_data['username'])
      list.append(u)
    else: 
      list = User.objects.filter(email=new_data['email'])
    return list

