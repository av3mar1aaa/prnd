# This Python file uses the following encoding: utf-8
import datetime, re
from .acttypes import *
from prnd.legacy import validators
from prnd.legacy import forms
from prnd.activity.models import *
from prnd.calculator.models import SelectedJournal
from django.contrib.auth.models import User, Group 
from prnd.activity.userreports import *
from prnd.register.djangohacks import IntegerField

class isValidJName(object):
  def __init__(self, field_name, name):
    self.field_name, self.name = field_name, name

  def __call__(self, field_data, all_data):
    if int(all_data[self.field_name]) != 0:
      s = 'Вы уже выбрали %s из списка.' % self.name
      raise validators.ValidationError(s)
    return


class IsIntegerInRange(object):
 def __init__(self, from_num, to_num):
   self.from_num, self.to_num = from_num, to_num
   self.always_test = True

 def __call__(self, field_data, all_data):
   integer_re = re.compile(r'^-?\d+$')

   if not integer_re.search(field_data) or int(field_data)<self.from_num or int(field_data)>self.to_num:
     s = "Введите число от %d до %d" %(self.from_num, self.to_num)
     raise validators.ValidationError(s)

class isValidLength(object):
  def __init__(self, maxlength):
    self.maxlength = maxlength

  def __call__(self, data, all_data):
    if data and self.maxlength and len(str(data)) > self.maxlength:
      s = "Длина текста не должна превышать %s символов" % self.maxlength
      raise validators.ValidationError(s)
  
class submitted_check(object):
  def __init__(self, owner_id, modifier_id):
    self.owner_id = int(owner_id)
    self.modifier_id = int(modifier_id)

  def __call__(self, field_data, all_data):
    year = int(field_data)
    if not can_add_or_modify_activity(self.modifier_id, self.owner_id, year):
      s = "Вы не можете менять отчет за этот год"
      raise validators.ValidationError(s)
 
  
def is_valid_year(field_data, all_data):
  to_year = datetime.date.today().year+1
  if int(field_data)<2000 or int(field_data)>to_year:
    raise validators.ValidationError("Введите число от 2000 до %d" %to_year)
    
class is_conference_name_needed(object):
  def __init__(self):
    self.always_test = True

  def  __call__(self, field_data, all_data):
    if int(all_data['conftype']) == 4 or int(all_data['conftype']) == 5:
      if not field_data:
        return
      else:
        raise validators.ValidationError("Для доклада на заседании название конференции не требуется.")
    elif field_data.isspace():
      raise validators.ValidationError("Обязательное поле")
 
class RequiredIfEditingtypeEquals2(object):
  def __init__(self):
    self.always_test = True

  def  __call__(self, field_data,all_data):
    if int(all_data["editingtype"]) == 1:
      if not field_data or field_data.isspace():
        raise validators.ValidationError("Обязательное поле") 
 
def is_valid_authornum(field_data, all_data):
  if int(field_data)<1 or int(field_data)>100:
    raise validators.ValidationError("Введите число от 1 до 100")

  if "authors" not in all_data:
    return
    
  authors = all_data["authors"]
  authorsnum = len(re.findall(",", authors))

  if int(authorsnum) >= int(field_data):
    raise validators.ValidationError("Кол-во автором меньше кол-ва имен авторов")
 

def is_valid_pages(field_data, all_data):
  regexp = re.compile(r"(?P<first>\d+)-(?P<last>\d+)")
  r = regexp.search(field_data)
  if not r or int(r.group(1)) > int(r.group(2)):
    raise validators.ValidationError("Введите два числа (второе не меньше первого) через дефис")
    
def is_valid_grif(field_data, all_data):
  if int(field_data) == 0 and len(all_data['isbn']) == 0:
    raise validators.ValidationError("Должен быть либо гриф, либо ISBN.")

def is_valid_further_affiliation(field_data, all_data):
  if int(all_data["suptype"]) == 1 and ((not field_data) or (field_data.isspace()) or (len(field_data)==0)):
    raise validators.ValidationError("Необходимо заполнить институт (или место работы), в аспирантуру которого поступил дипломник.")
    
def is_valid_further_affiliation2(field_data, all_data):
  if int(field_data) == 1 and len(all_data['further_affiliation']) == 0:
    raise validators.ValidationError("Необходимо заполнить институт (или место работы), в аспирантуру которого поступил дипломник.")


def is_valid_monograph_coef(field_data, all_data):
  if float(field_data) < 2.0 or float(field_data) > 3.0:
    raise validators.ValidationError("Введите число от 2.0 до 3.0.")
   
def _is_russian_char(c):
  """Check if character is Russian (Cyrillic)."""
  return 'А' <= c <= 'Я' or 'а' <= c <= 'я'

def _sort_key(item):
  """Sort key: Russian names first, then alphabetically."""
  name = item[1].upper() if item[1] else ""
  first_char = name[0] if name else ""
  is_rus = _is_russian_char(first_char) if first_char else False
  # Russian first (0), then others (1), then alphabetically
  return (0 if is_rus else 1, name)

def get_list(name_list):
  result = []
  for name in name_list:
    for s in SelectedJournal.objects.filter(type=name):
      result.append((s.id, s.fullname))
  result.sort(key=_sort_key)
  result.insert(0, (0, "нет в списке"))
  return result

class MonographForm(forms.Manipulator):
  def __init__(self, owner_id, modifier_id):
    list = get_list(['P'])
    self.fields = (
      forms.TextField   (field_name='name',    length=30, maxlength=500, is_required=True),
      forms.TextField   (field_name='authors', length=30, maxlength=500, is_required=True),
      IntegerField(field_name="authornum",length=4,  maxlength=4, is_required=True, validator_list=[is_valid_authornum]),
      forms.SelectField (field_name='journal_id',choices=list,             is_required=True ),
      forms.TextField   (field_name='journal',   length=30, maxlength=500, validator_list=[isValidJName('journal_id', 'издательство'), validators.RequiredIfOtherFieldEquals('journal_id','0', "Это поле должно быть заполнено, поскольку Вы не выбрали журнал из списка")], ),
      forms.TextField   (field_name="pagenum", length=4,  maxlength=4,   is_required=True, validator_list=[IsIntegerInRange(1, 40)]),
      forms.TextField   (field_name='isbn',    length=30, maxlength=500),
      forms.SelectField (field_name='grif',    choices=monograph_grif_types, validator_list=[is_valid_grif]),
      IntegerField(field_name="year",    length=4,  maxlength=4,   is_required=True, validator_list=[is_valid_year, submitted_check(owner_id, modifier_id)]),
      forms.TextField   (field_name='note',    length=30, maxlength=500, is_required=False),
      forms.FloatField  (field_name='coef',    max_digits=4, decimal_places=2, validator_list=[is_valid_monograph_coef]),
    )
    
  def form2object(self, form_data, u_id):
    if 'coef' in form_data and form_data['coef']:
      coef    = form_data['coef']
    else:
      if int(form_data['journal_id']) > 0:
        coef    = 3.0
      else:
        coef    = 2.0
    
    m = Monograph(
      user_id   = u_id,
      name      = form_data['name'],
      authors   = form_data['authors'],
      authornum = form_data['authornum'],
      journal   = form_data['journal'],
      journal_id= form_data['journal_id'],
      pagenum   = form_data['pagenum'],
      grif      = form_data['grif'],
      isbn      = form_data['isbn'],
      year      = form_data['year'],
      note      = form_data['note'],
      coef      = coef,
    )
    return m
    
class PublicationForm(forms.Manipulator):
  def __init__(self, owner_id, modifier_id):
    list = get_list(['A', 'B'])
    self.fields = (
      forms.TextField   (field_name='name',      length=30, maxlength=500, is_required=True),
      IntegerField(field_name="authornum", length=4,  maxlength=4,   is_required=True, validator_list=[is_valid_authornum]),
      forms.TextField   (field_name='authors',   length=30, maxlength=500, is_required=True),
      forms.SelectField (field_name='pubtype',   choices=publication_types, is_required=True),
      forms.SelectField (field_name='language',  choices=language_types, is_required=True),
      forms.SelectField (field_name='journal_id',choices=list,      is_required=True ),
      forms.TextField   (field_name='journal',   length=30, maxlength=500, validator_list=[isValidJName('journal_id', 'журнал'), validators.RequiredIfOtherFieldEquals('journal_id','0', "Это поле должно быть заполнено, поскольку Вы не выбрали журнал из списка")], ),
      forms.TextField   (field_name='volume',    length=30, maxlength=500, is_required=False),
      forms.TextField   (field_name='jnumber',   length=30, maxlength=500, is_required=False),
      forms.TextField   (field_name='pages',     length=30, maxlength=500, is_required=False, validator_list=[is_valid_pages]),
      IntegerField(field_name="year",      length=4,  maxlength=4,   is_required=True, validator_list=[is_valid_year, submitted_check(owner_id, modifier_id)]),
      forms.TextField   (field_name='note',      length=30, maxlength=500, is_required=False),
      forms.TextField   (field_name='webpage',   length=30, maxlength=500, is_required=False),
      forms.TextField   (field_name='idnumber',  length=30, maxlength=500, is_required=False),
      forms.FloatField  (field_name='coef',      max_digits=4, decimal_places=2),
      forms.CheckboxField  (field_name='instcoauthors'),
    )
    
  def form2object(self, form_data, u_id):
    p = Activity(
      user_id      = u_id,
      name         = form_data['name'],
      authors      = form_data['authors'],
      year         = form_data['year'],
      note         = form_data['note'],
      webpage      = form_data['webpage'],
      idnumber     = form_data['idnumber'],
      journal      = form_data['journal'],
      journal_id   = form_data['journal_id'],
      volume       = form_data['volume'],
      jnumber      = form_data['jnumber'],
      authornum    = form_data['authornum'],
      pages        = form_data['pages'],
      pubtype      = form_data['pubtype'],
      language     = form_data['language'],
      instcoauthors= form_data['instcoauthors'],
    )
    return p


class ConferenceForm(forms.Manipulator):
  def __init__(self, owner_id, modifier_id):
    self.fields = (
      forms.SelectField (field_name="conftype",  choices=conference_types),
      forms.TextField   (field_name='name',      length=30, maxlength=500, validator_list=[is_conference_name_needed()]),
      forms.TextField   (field_name='place',     length=30, maxlength=500, is_required=False),
      forms.TextField   (field_name='dates',     length=30, maxlength=500, is_required=False),            
      forms.TextField   (field_name='authors',   length=30, maxlength=500, is_required=True),
      IntegerField(field_name="authornum", length=4,  maxlength=4, is_required=True, validator_list=[is_valid_authornum]),
      forms.TextField   (field_name='talktitle', length=30, maxlength=500, is_required=True),
      IntegerField(field_name="year",      length=4,  maxlength=4,   is_required=True, validator_list=[is_valid_year, submitted_check(owner_id, modifier_id)]),
      forms.TextField   (field_name='note',      length=30, maxlength=500, is_required=False),
    )
      
  def form2object(self, form_data, u_id):
    c = Conference(
      user_id      = u_id,
      name         = form_data['name'],
      authors      = form_data['authors'],
      authornum    = form_data['authornum'],
      year         = form_data['year'],
      note         = form_data['note'],
      talktitle    = form_data['talktitle'],
      conftype     = form_data['conftype'],
      place        = form_data['place'],
      dates        = form_data['dates'],
      )
    return c

class PatentForm(forms.Manipulator):
  def __init__(self, owner_id, modifier_id):
    self.fields = (
      forms.TextField   (field_name='name',      length=30, maxlength=500, is_required=True),
      IntegerField(field_name="authornum", length=4,  maxlength=4,   is_required=True, validator_list=[is_valid_authornum]),
      forms.TextField   (field_name='authors',   length=30, maxlength=500, is_required=True),
      forms.TextField   (field_name='number',   length=30, maxlength=500, is_required=True),
      forms.TextField   (field_name='place',    length=30, maxlength=500, is_required=True),
      IntegerField(field_name="year",      length=4,  maxlength=4,   is_required=True, validator_list=[is_valid_year, submitted_check(owner_id, modifier_id)]),
      forms.TextField   (field_name='note',      length=30, maxlength=500, is_required=False),
    )
      
  def form2object(self, form_data, u_id):
    p = Patent(
      user_id      = u_id,
      name         = form_data['name'],
      authors      = form_data['authors'],
      year         = form_data['year'],
      note         = form_data['note'],
      authornum    = form_data['authornum'],
      number       = form_data['number'],
      place        = form_data['place'],
      )
    return p

class CourseForm(forms.Manipulator):
  def __init__(self, owner_id, modifier_id):
    self.fields = (
      forms.TextField   (field_name='name',    length=30, maxlength=500, is_required=True),
      IntegerField(field_name="year",    length=4,  maxlength=4,   is_required=True, validator_list=[is_valid_year, submitted_check(owner_id, modifier_id)]),
      forms.TextField   (field_name='note',    length=30, maxlength=500, is_required=False),
      forms.SelectField (field_name='coursetype', choices=course_types),
      forms.SelectField (field_name='duration',   choices=course_duration_types),
    )
      
  def form2object(self, form_data, u_id):
    c = Course(
      user_id   = u_id,
      name      = form_data['name'],
      coursetype= form_data['coursetype'],
      year      = form_data['year'],
      note      = form_data['note'],
      duration  = form_data['duration']
    )
    return c
    
class SupervisingForm(forms.Manipulator):
  def __init__(self,owner_id, modifier_id):
    self.fields = (
      forms.TextField   (field_name='name',    length=30, maxlength=500, is_required=True),
      IntegerField(field_name="year",    length=4,  maxlength=4,   is_required=True, validator_list=[is_valid_year, submitted_check(owner_id, modifier_id)]),
      IntegerField(field_name="authornum",length=4, maxlength=4,   is_required=True, validator_list=[is_valid_authornum]),
      forms.TextField   (field_name='note',    length=30, maxlength=500, is_required=False),
      forms.TextField   (field_name='institute',length=30, maxlength=500, is_required=True),
      forms.TextField   (field_name='subject',  length=30, maxlength=500, is_required=True),
      forms.TextField   (field_name='further_affiliation',  length=30, maxlength=500, validator_list=[is_valid_further_affiliation]),
      forms.SelectField (field_name='suptype', choices=supervising_types, validator_list=[is_valid_further_affiliation2]),
    )
      
  def form2object(self, form_data, u_id):
    s = Supervising(
      user_id   = u_id,
      name      = form_data['name'],
      suptype   = form_data['suptype'],
      authornum = form_data['authornum'],
      subject   = form_data['subject'],
      institute = form_data['institute'],
      year      = form_data['year'],
      note      = form_data['note'],
      further_affiliation = form_data['further_affiliation']
    )
    return s
    

class OrgWorkForm(forms.Manipulator):
  def __init__(self,owner_id, modifier_id):
    self.fields = (
      forms.TextField   (field_name='name',    length=30, maxlength=500, is_required=True),
      IntegerField(field_name="year",    length=4,  maxlength=4,   is_required=True, validator_list=[is_valid_year, submitted_check(owner_id, modifier_id)]),
      forms.TextField   (field_name='place',     length=30, maxlength=500, is_required=False),
      forms.TextField   (field_name='dates',     length=30, maxlength=500, is_required=False),            
      forms.TextField   (field_name='note',    length=30, maxlength=500, is_required=False),
      forms.SelectField (field_name='worktype', choices=orgwork_types),
    )
      
  def form2object(self, form_data, u_id):
    o = OrgWork(
      user_id   = u_id,
      name      = form_data['name'],
      worktype  = form_data['worktype'],
      year      = form_data['year'],
      place     = form_data['place'],
      dates     = form_data['dates'],
      note      = form_data['note']
    )
    return o

class OpposingForm(forms.Manipulator):
  def __init__(self,owner_id, modifier_id):
    self.fields = (
      forms.TextField   (field_name='name',    length=30, maxlength=500, is_required=True),
      forms.TextField   (field_name='institute',length=30, maxlength=500, is_required=True),
      forms.TextField   (field_name='subject',  length=30, maxlength=500, is_required=True),
      IntegerField(field_name="year",    length=4,  maxlength=4,   is_required=True, validator_list=[is_valid_year, submitted_check(owner_id, modifier_id)]),
      forms.TextField   (field_name='note',    length=30, maxlength=500, is_required=False),
      forms.SelectField (field_name='opptype', choices=opposing_types),
    )
      
  def form2object(self, form_data, u_id):
    o = Opposing(
      user_id   = u_id,
      name      = form_data['name'],
      institute = form_data['institute'],
      opptype   = form_data['opptype'],
      subject   = form_data['subject'],
      year      = form_data['year'],
      note      = form_data['note']
    )
    return o

class StudentSupervisingForm(forms.Manipulator):
  def __init__(self, owner_id, modifier_id):
    self.fields = (
      forms.TextField   (field_name='name',    length=30, maxlength=500, is_required=True),
      IntegerField(field_name="year",    length=4,  maxlength=4,   is_required=True, validator_list=[is_valid_year, submitted_check(owner_id, modifier_id)]),
      forms.TextField   (field_name='note',    length=30, maxlength=500, is_required=False),
    )
      
  def form2object(self, form_data, u_id):
    s = StudentSupervising(
      user_id   = u_id,
      name      = form_data['name'],
      year      = form_data['year'],
      note      = form_data['note']
    )
    return s
    
report_types = (
  (1, "цветная страница"),
  (2, "черно-белая страница"),  
)

class UserReportForm(forms.Manipulator):
  def __init__(self, user):
    choices = YearStatistics.STATUS_CHOICES[0:get_maximal_report_status_choice(user)+1]
    
    self.fields = (
    forms.SelectField    (field_name='status',        choices=choices ),
    forms.FloatField     (field_name='coef_modifier', max_digits=4, decimal_places=3),
    forms.FloatField     (field_name='additional_coef',max_digits=8, decimal_places=3),
    forms.LargeTextField (field_name='reason',        cols=80, rows=3, validator_list=[isValidLength(500)] ),
    forms.CheckboxField  (field_name='calcasmaximum'),
    forms.LargeTextField (field_name='detailed_report',cols=80,rows=30,is_required=True, validator_list=[isValidLength(500000)]),
    )

  def save(self, ys, form_data):
    if 'coef_modifier' in form_data and form_data['coef_modifier'] != None:
      ys.coef_modifier = form_data['coef_modifier']
    if 'additional_coef' in form_data and form_data['additional_coef'] != None:
      ys.additional_coef = form_data['additional_coef']
    if 'status' in form_data and form_data['status'] != None:
      ys.status = form_data['status']
    if 'reason' in form_data and form_data['reason'] != None:
      ys.reason = form_data['reason']
    if 'detailed_report' in form_data and form_data['detailed_report'] != None:
      ys.detailed_report = form_data['detailed_report']
    if 'calcasmaximum' in form_data and form_data['calcasmaximum'] != None:
      ys.calcasmaximum = form_data['calcasmaximum']
      
class ReportForm(forms.Manipulator):
  def __init__(self):
    self.fields = (
      IntegerField(field_name="yearfrom",    length=4,  maxlength=4,   is_required=True, validator_list=[is_valid_year]),
      IntegerField(field_name="yearto",      length=4,  maxlength=4,   is_required=True, validator_list=[is_valid_year]),
      forms.CheckboxField  (field_name='wbreport'),
    )

class AttestationForm(forms.Manipulator):
  def __init__(self):
    self.fields = (
      IntegerField(field_name="yearfrom",    length=4,  maxlength=4,   is_required=True, validator_list=[is_valid_year]),
      IntegerField(field_name="yearto",      length=4,  maxlength=4,   is_required=True, validator_list=[is_valid_year]),
    )
  
    
class EditingForm(forms.Manipulator):
  def __init__(self, owner_id, modifier_id):

    self.fields = (
      forms.TextField   (field_name='name',       length=30, maxlength=500, is_required=True),
      forms.TextField   (field_name='journal',     length=30, maxlength=500, is_required=True),
      forms.TextField   (field_name='volume',     length=10, maxlength=500, validator_list=[RequiredIfEditingtypeEquals2()]),
      IntegerField      (field_name="year",       length=4,  maxlength=4,   is_required=True, validator_list=[is_valid_year, submitted_check(owner_id, modifier_id)]),
      forms.TextField   (field_name='note',        length=30, maxlength=500, is_required=False),
      forms.SelectField (field_name='editingtype', choices=editing_types),
    )
      
  def form2object(self, form_data, u_id):
    e = Editing(
      user_id      = u_id,
      name         = form_data['name'],
      volume       = form_data['volume'],
      journal      = form_data['journal'],
      editingtype  = form_data['editingtype'],
      year         = form_data['year'],
      note         = form_data['note']
    )
    return e

class EditingCollegiumForm(forms.Manipulator):
  def __init__(self, owner_id, modifier_id):
    list = get_list(['A', 'B'])

    self.fields = (
      forms.SelectField (field_name='journal_id',choices=list,             is_required=True ),
      IntegerField      (field_name="year",       length=4,  maxlength=4,   is_required=True, validator_list=[is_valid_year, submitted_check(owner_id, modifier_id)]),
      forms.TextField   (field_name='note',        length=30, maxlength=500, is_required=False),
    )
      
  def form2object(self, form_data, u_id):
    ec = EditingCollegium(
      user_id      = u_id,
      journal_id   = form_data['journal_id'],
      year         = form_data['year'],
      note         = form_data['note']
    )
    return ec

class GrantForm(forms.Manipulator):
  def __init__(self, owner_id, modifier_id):
    
    self.fields = (
      forms.TextField   (field_name='name',       length=30, maxlength=500, is_required=True),
      forms.TextField   (field_name='role',       length=30, maxlength=500, is_required=True),
      IntegerField      (field_name="year",       length=4,  maxlength=4,   is_required=True, validator_list=[is_valid_year, submitted_check(owner_id, modifier_id)]),
      forms.TextField   (field_name='note',       length=30, maxlength=500, is_required=False),
    )
      
  def form2object(self, form_data, u_id):
    g = Grant(
      user_id      = u_id,
      name         = form_data['name'],
      role         = form_data['role'],      
      year         = form_data['year'],
      note         = form_data['note']
    )
    return g

class AwardForm(forms.Manipulator):
  def __init__(self, owner_id, modifier_id):
    
    self.fields = (
      forms.TextField   (field_name='name',       length=30, maxlength=500, is_required=True),
      IntegerField      (field_name="year",       length=4,  maxlength=4,   is_required=True, validator_list=[is_valid_year, submitted_check(owner_id, modifier_id)]),
      forms.TextField   (field_name='note',       length=30, maxlength=500, is_required=False),
    )
      
  def form2object(self, form_data, u_id):
    a = Award(
      user_id      = u_id,
      name         = form_data['name'],
      year         = form_data['year'],
      note         = form_data['note']
    )
    return a

#class MassSubscriptionForm(forms.Manipulator):
#  def __init__(self, user):
#    choices = YearStatistics.STATUS_CHOICES[0:get_maximal_report_status_choice(user)+1]
#    
#    self.fields = (
#    forms.IntegerField   (field_name="yearto",      length=4,  maxlength=4,   is_required=True, validator_list=[is_valid_year]),
#    forms.SelectField    (field_name='status',        choices=choices ),
#    )
#
#  def save(self, ys, form_data):
#    if form_data.has_key('status') and form_data['status'] != None:
#      ys.status = form_data['status']
#    if form_data.has_key('year') and form_data['year'] != None:
#      ys.status = form_data['year']
