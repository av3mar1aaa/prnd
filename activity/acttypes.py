# This Python file uses the following encoding: utf-8
from prnd.calculator.models import SelectedJournal
from django.shortcuts import get_object_or_404
from prnd.activity.models import *
from prnd.activity.forms import *
from prnd.calculator.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from decimal import *

act_type_num = 12
publication_type, monograph_type, conference_type, course_type, patent_type, supervising_type, editing_type, orgwork_type, opposing_type, editing_collegium_type, grant_type, award_type = list(range(act_type_num))

# the order of these arrays is important!
activity_name     = ["publications", "monographs", "conferences", "courses", "patents", "supervising", "editing"       , "orgwork",             "opposing",      "editingcollegium",               "grants", "awards"]                     
activity_rusname1 = ["публикация",   "монография", "доклад",      "курс",    "патент",  "руководство", "редактирование", "орг.-научная работа", "оппонирование", "работа в составе ред. коллегий", "грант",  "награды"]
activity_rusname2 = ["Публикации",   "монографии", "Доклады на научных мероприятиях",     "Курсы лекций и преподавание",   "Патенты", "Научное руководство", "Научное редактирование", "Организация научных мероприятий", "оппонирование", "работа в составе ред. коллегий", "Гранты", "Награды и премии"]

act_select_types = (
  (0, "публикации"),
  (1, "монографии"),
  (2, "доклады"),
  (3, "курсы"),
  (4, "патенты"),
  (5, "руководство"),
  (6, "редактирование"),
  (7, "орг.-научная работа"),
  (8, "оппонирование"),
  (9, "работа в составе ред. коллегий"),  
  (10, "гранты"),
  (11, "награды"),
)

publication_types = (
  (0, "публикация в журнале"),
  (1, "публикация в продолжающемся издании или книге"),
  (2, "препринт"),
  (3, "публикация в материалах научных мероприятий"),
  (4, "публикация в зарегистрированных научных электронных изданиях"),  
  (5, "научно-популярная книга или статья"),  
  (6, "другая"),  
)

language_types = (
  (0, "русский"),
  (1, "иностранный"),
)

conference_types = (
  (0, "Устный доклад на российской конференции"),
  (1, "Устный доклад на международной конференции"),
  (2, "Приглашенный доклад на российской конференции"),
  (3, "Приглашенный доклад на международной конференции"),
  (4, "Доклад на заседании Общеинститутского семинара ПОМИ"),
  (5, "Доклад на заседании Петербургского математического общества"),
)

course_types = (
  (0, "Курс, читаемый впервые"),
  (1, "Курс, читаемый второй год"),
  (2, "Курс, читаемый более двух лет"),
  (3, "Специализированный студенческий семинар"),
)

course_duration_types = (
  (0, "один семестр"),
  (1, "два семестра"),
)

supervising_types = (
  (0, "Руководство лицом, защитившим кандидатскую диссертацию"),
  (1, "Руководство дипломной работой или магистерской диссертацией"),
  (2, "Консультирование соискателя ученой степени, защитившего докторскую диссертацию"),
)

orgwork_types = (
  (0, "Работа в составе прогр./орг. комитета российской конференции"),
  (1, "Работа в составе прогр./орг. комитета международной конференции"),  
)

opposing_types = (
  (0, "Оппонирование кандидатской диссертации"),
  (1, "Оппонирование докторской диссертации"),  
  (2, "Внешний отзыв на кандидатскую диссертацию"),
  (3, "Внешний отзыв на докторскую диссертацию"),
)

editing_types = (
  (0, "Редактирование книги"),
  (1, "Редактирование тома в продолжающемся издании"),
  (2, "Редактирование трудов конференции"),
)

monograph_grif_types = (
  (0, "нет"),
  (1, "есть"),
)

def type2name(act_type):
  if act_type < 0 or act_type > act_type_num:
    raise Http404
  return activity_name[act_type] 
  
def type2rusname1(act_type):
  if act_type < 0 or act_type > act_type_num:
    raise Http404
  return activity_rusname1[act_type] 
  
def type2rusname2(act_type):
  if act_type < 0 or act_type > act_type_num:
    raise Http404
  return activity_rusname2[act_type] 
  
def name2type(act_name):
  return activity_name.index(act_name)
 
def act2txt(act_type, act):
  s = ""
  
  if act_type == publication_type:
    s += act.authors + ", "
    s += act.name + ". "
    if act.journal != "":
      s += act.journal + ", "
    else:
      try:
        s += SelectedJournal.objects.get(id=act.journal_id).fullname + ", "
      except ObjectDoesNotExist:
        s += "неизвестный журнал, "
    if act.volume:
      s += "том " + act.volume + ", "
    if act.jnumber:
      s += "номер " + act.jnumber + ", "
    if act.pages:
      s += "стр. " + act.pages + ", "
    if act.idnumber:
      s += "identifikatsionnii nomer " + act.idnumber + ", "
  elif act_type == conference_type:
    s += act.authors + ", "
    s += act.talktitle + ". "
    s += conference_types[act.conftype][1] + " " + act.name + ", "
  elif act_type == patent_type:
    s += act.authors + ". "
    s += act.name + ". "
  elif act_type == monograph_type:
    s += act.authors + ". "
    s += act.name + ". "
    if act.journal != "":
      s += act.journal + ", "
    else:
      try:
        s += SelectedJournal.objects.get(id=act.journal_id).fullname + ", "
      except ObjectDoesNotExist:
        s += "неизвестное издательство, "
    if act.isbn:
      s += "ISBN " + act.isbn + ", "
    s += str(act.pagenum) + " печ. лист., "
  elif act_type == course_type:
    s += act.name + ". </i>"
    s += course_types[act.coursetype][1] + " (" + course_duration_types[act.duration][1] + "), "
  elif act_type == supervising_type:
    s += supervising_types[act.suptype][1] + ". "
    s += "Фамилия руководимого лица: " + act.name
    s += "Организация: " + act.institute
    if act.further_affiliation and act.further_affiliation != "":
      s += "поступил в " + act.further_affiliation
    s += ", "
  elif act_type == editing_type:
    s += editing_types[act.editingtype][1] + ". "   
    if act.journal != "":
      s += act.journal
  elif act_type == editing_collegium_type:
    try:
      s += SelectedJournal.objects.get(id=act.journal_id).fullname + ", "
    except ObjectDoesNotExist:
      s += "неизвестный журнал, "
  elif act_type == orgwork_type:
    s += orgwork_types[act.worktype][1] + " " + act.name + ", "
  elif act_type == opposing_type:
    s += opposing_types[act.opptype][1] + ". "
    s += "Фамилия защищавшегося: " + act.name
    s += "Организация: " + act.institute
    s += "Тема: " + act.subject
    s += ", "
  #elif act_type == studsupervising_type:
    #s += "<i>" + act.name + ". </i>"
  elif act_type == grant_type:
    s += act.name + "(" + act.role + "), "
  elif act_type == award_type:
    s += act.name + ", "


  s += act.year + " г. "
  if act.note:
    s += " (" + act.note + ")"
    
  if act_type == publication_type:
    if act.webpage:
      s += "ссылка:" + act.webpage
    s += "(" + publication_types[act.pubtype][1] + ")"

  return s

  
def act2html(act_type, act):
  s = ""
  
  if act_type == publication_type:
#    #s += "<b>" + act.authors + "</b>"
#    s += act.authors + "."
#    
#    s += "<br><i>" + act.name + ".</i>"
#    if act.journal != "":
#      s += "<br>" + act.journal + ", "
#    else:
#      try:
#        s += "<br>" + SelectedJournal.objects.get(id=act.journal_id).fullname + ", "
#      except ObjectDoesNotExist:
#        s += "<br>" + "неизвестный журнал, "
#    if act.volume:
#      if act.language == 0:
#        s += "том " 
#      else:
#        s += "Vol. "
#      s += act.volume + ", "
#    if act.jnumber:
#      if act.language == 0:
#        s += "номер "
#      else:
#        s += "no. "
#      s += act.jnumber + ", "
#    if act.pages:
#      if act.language == 0:
#        s += "стр. " 
#      else:
#        s += "P. "
#      s += act.pages + ", "
#    if act.idnumber:
#      s += "идентификационный номер " + act.idnumber + ", "

#  if act_type == publication_type:
#    if act.webpage:
#      s += "<br>(<a href=" + act.webpage + ">" + act.webpage + "</a>)"
#    s += "<br>(" + publication_types[act.pubtype][1] + ")"

##### pechat' publikatsii po gostu:

    s += act.authors + ". " + act.name + " // " # ".&mdash; " + act.year + ".&mdash;"
    if act.journal != "":
      s += act.journal
    else:
      try:
        s += SelectedJournal.objects.get(id=act.journal_id).fullname
      except ObjectDoesNotExist:
        s += "неизвестн"
    s += ".&mdash; " + act.year + ".&mdash; "        

    if act.journal == "":
      try:
        journal = SelectedJournal.objects.get(id=act.journal_id)
        jtype = journal.type
# hack
      except ObjectDoesNotExist:
        jtype = 'C'
    else:
      jtype = 'C'



    if act.volume:
      if act.language == 0:
        s += "том " 
      else:
        s += "Vol. "
      s += act.volume
    if act.jnumber:
      if act.language == 0:
        s += ", номер "
      else:
        s += ", no. "
      s += act.jnumber
    s += ".&mdash; "
    if act.pages:
      if act.language == 0:
        s += "Стр. " 
      else:
        s += "P. "
      s += act.pages + "."
    if act.idnumber:
      s += " Идентификационный номер " + act.idnumber + ", "
    if act.webpage:
      s += "<br>(<a href=" + act.webpage + ">" + act.webpage + "</a>)"
    #s += "<br>(" + publication_types[act.pubtype][1] + ")"
    
    #s += "<br>(type="+jtype+")"


    s.replace(" .", ".")

  elif act_type == conference_type:
    s += "<b>" + act.authors + ".</b>"
    s += "<br><i>" + act.talktitle + ". </i>"
    s += "<br>" + conference_types[act.conftype][1] + " " + act.name + ", "
    if act.place:
      s += "место проведения: " + act.place + ", "
    if act.dates:
      s += "время проведения: " + act.dates + ", "
  elif act_type == patent_type:
    s += "<b>" + act.authors + ".</b>"
    s += "<br><i>" + act.name + ". </i>"
    s += "<br>"
    if act.number:
      s += "номер: " + act.number + ", "
    if act.place:
      s += "место регистрации: " + act.place + ", "
  elif act_type == monograph_type:
    s += "<b>" + act.authors + ".</b>"
    s += "<br><i>" + act.name + ". </i>"
    if act.journal != "":
      s += "<br>" + act.journal + ", "
    else:
      try:
        s += "<br>" + SelectedJournal.objects.get(id=act.journal_id).fullname + ", "
      except ObjectDoesNotExist:
        s += "<br>" + "неизвестное издательство, "
    if act.isbn:
      s += "ISBN " + act.isbn + ", "
    s += "гриф Минобрнауки: " + monograph_grif_types[act.grif][1] + ", "
    s += str(act.pagenum) + " печ. лист., "
  elif act_type == course_type:
    s += "<i>" + act.name + ". </i>"
    s += "<br>" + course_types[act.coursetype][1] + " (" + course_duration_types[act.duration][1] + "), "
  elif act_type == supervising_type:
    s += supervising_types[act.suptype][1] + "."
    s += "<br>Фамилия руководимого лица: " + act.name
    s += "<br>Тема: " + act.subject
    s += "<br>Организация: " + act.institute
    if act.further_affiliation and act.further_affiliation != "":
      s += "<br>Поступил в " + act.further_affiliation
    s += ", "
  elif act_type == editing_type:
    s += editing_types[act.editingtype][1] + " " + act.name + "."
    s += "<br>Издательство: " + act.journal + ", "
    if act.volume:
      s += "том " + act.volume + ", "
  elif act_type == editing_collegium_type:
    try:
      s += SelectedJournal.objects.get(id=act.journal_id).fullname + ", "
    except ObjectDoesNotExist:
      s += "неизвестный журнал, "
  elif act_type == orgwork_type:
    s += orgwork_types[act.worktype][1] + " " + act.name + ", "
    if act.place:
      s += "место проведения: " + act.place + ", "
    if act.dates:
      s += "время проведения: " + act.dates + ", "
  elif act_type == opposing_type:
    s += opposing_types[act.opptype][1] + "."
    s += "<br>Фамилия защищавшегося: " + act.name
    s += "<br>Организация: " + act.institute
    s += "<br>Тема: " + act.subject
    s += ", "
  elif act_type == grant_type:
    s += act.name + "(" + act.role + "), "
  elif act_type == award_type:
    s += act.name + ", "
  
  if act_type != publication_type:
    s += act.year + " г."
  if act.note:
    s += " (" + act.note + ")"
    
#  if act_type == publication_type:
#    if act.webpage:
#      s += "<br>(<a href=" + act.webpage + ">" + act.webpage + "</a>)"
#    s += "<br>(" + publication_types[act.pubtype][1] + ")"

  return s

def normalize_by_authornum(act, cost, round10=True):
  if act.authornum <= 0.0:
    return cost;
  else:
    n = act.authornum
    if round10 and n > 10.0:
      n = 10.0

    return round(float(cost)/float(n), 3)

def get_activity_cost(act_type, act):
  if act_type == publication_type:
    if act.journal == "":
      try:
        journal = SelectedJournal.objects.get(id=act.journal_id)
        jtype = journal.type
# hack
      except ObjectDoesNotExist:
        jtype = 'C'
    else:
     jtype = 'C'

    name = "Journal %s" % jtype
    
    # ran'sche bilo tak:
    #if act.pubtype <= 2: 
    #  if jtype == 'A':
    #    cost = 30.0
    #  elif jtype == 'B':
    #    cost = 15.0
    #  else:
    #    cost = 6.0
    #else:
    #  cost = 0.0
    ##cost = Cost.objects.get(note=name).value 

    if jtype == 'A':
      cost = 30.0
    elif jtype == 'B':
      cost = 15.0
    else:
      cost = 6.0
    
  
    return normalize_by_authornum(act, cost)
  elif act_type == conference_type:
    return normalize_by_authornum(act, 15.0)
    # ran'sche bilo tak; izmeneno 03.02.2012 (hotya dolgno bilo aj 27.01.2011)
    #if act.conftype == 0 or act.conftype == 4 or act.conftype == 5:
    #  return normalize_by_authornum(act, 4.0)
    #elif act.conftype == 1:
    #  return normalize_by_authornum(act, 6.0)
    #elif act.conftype == 2:
    #  return normalize_by_authornum(act, 20.0)
    #else:
    #  return normalize_by_authornum(act, 30.0)
  elif act_type == patent_type:
    return normalize_by_authornum(act, 20.0)
  elif act_type == monograph_type:
    return normalize_by_authornum(act, act.coef*act.pagenum, False)
  elif act_type == course_type:
    if act.coursetype == 0:
      return 20.0*(act.duration+1)
    elif act.coursetype == 1:
      return 10.0*(act.duration+1)
    else:
      return 5.0*(act.duration+1)
  elif act_type == supervising_type:
    if act.suptype == 0:
      return normalize_by_authornum(act, 45.0)
    elif act.suptype == 1:
      return normalize_by_authornum(act, 15.0)
    elif act.suptype == 2:
      return normalize_by_authornum(act, 45.0)
    else:
      return 0.0
  elif act_type == editing_type:
    if act.editingtype == 0:
      return 0.0 #10.0
    elif act.editingtype == 1:
      return 0.0 #10.0
    elif act.editingtype == 2:
      return 0.0 #10.0
  elif act_type == editing_collegium_type:
    try:
      journal = SelectedJournal.objects.get(id=act.journal_id)
      jtype = journal.type
    except ObjectDoesNotExist:
      jtype = 'C'

    if jtype == 'A':
      cost = 0.0 #3.0
    elif jtype == 'B':
      cost = 0.0 #2.0
    else:
      cost = 0.0
      
    return cost
  elif act_type == orgwork_type:
    if act.worktype == 0:
      return 0.0 #4.0
    elif act.worktype == 1:
      return 0.0 #6.0      
  elif act_type == opposing_type:
    if act.opptype == 0:
      return 5.0 #10.0
    elif act.opptype == 1:
      return 5.0 #15.0
    elif act.opptype == 2:
      return 6.0
    elif act.opptype == 3:
      return 6.0
    else:
      assert False
  elif act_type == grant_type:
    return 0.0      
  elif act_type == award_type:
    return 0.0      
    
def get_activity_from_db(act_type, act_id):
  # Given type of table and id, finds the corresponding record.
  if act_type == publication_type:
    return get_object_or_404(Activity, pk=act_id)
  elif act_type == conference_type:
    return get_object_or_404(Conference, pk=act_id)
  elif act_type == patent_type:
    return get_object_or_404(Patent, pk=act_id)
  elif act_type == monograph_type:
    return get_object_or_404(Monograph, pk=act_id)
  elif act_type == course_type:
    return get_object_or_404(Course, pk=act_id)
  elif act_type == supervising_type:
    return get_object_or_404(Supervising, pk=act_id)
  elif act_type == editing_type:
    return get_object_or_404(Editing, pk=act_id)
  elif act_type == editing_collegium_type:
    return get_object_or_404(EditingCollegium, pk=act_id)
  elif act_type == orgwork_type:
    return get_object_or_404(OrgWork, pk=act_id)
  elif act_type == opposing_type:
    return get_object_or_404(Opposing, pk=act_id)
  elif act_type == grant_type:
    return get_object_or_404(Grant, pk=act_id)
  elif act_type == award_type:
    return get_object_or_404(Award, pk=act_id)
    
def get_detail_file_name(act_type):
  if act_type == publication_type:
    return "acts/publication_detail.html"
  elif act_type == conference_type:
    return "acts/conference_detail.html"
  elif act_type == patent_type:
    return "acts/patent_detail.html"
  elif act_type == monograph_type:
    return "acts/monograph_detail.html"
  elif act_type == course_type:
    return "acts/course_detail.html"
  elif act_type == supervising_type:
    return "acts/supervising_detail.html"
  elif act_type == editing_type:
    return "acts/editing_detail.html"
  elif act_type == editing_collegium_type:
    return "acts/editing_collegium_detail.html"
  elif act_type == orgwork_type:
    return "acts/orgwork_detail.html"
  elif act_type == opposing_type:
    return "acts/opposing_detail.html"
  elif act_type == grant_type:
    return "acts/grant_detail.html"
  elif act_type == award_type:
    return "acts/award_detail.html"

def get_activity_list(request, act_type):    
  return get_user_activity_list(request.user, act_type)
    
def get_user_activity_list(user, act_type):
  if act_type == publication_type:
    return user.activity_set.all()
  elif act_type == conference_type:
    return user.conference_set.all()
  elif act_type == patent_type:
    return user.patent_set.all()
  elif act_type == monograph_type:
    return user.monograph_set.all()
  elif act_type == course_type:
    return user.course_set.all()
  elif act_type == supervising_type:
    return user.supervising_set.all()
  elif act_type == editing_type:
    return user.editing_set.all()
  elif act_type == editing_collegium_type:
    return user.editingcollegium_set.all()
  elif act_type == orgwork_type:
    return user.orgwork_set.all()
  elif act_type == opposing_type:
    return user.opposing_set.all()
  elif act_type == grant_type:
    return user.grant_set.all()
  elif act_type == award_type:
    return user.award_set.all()
    
def get_user_activity_list_on_given_year(user, act_type, year):    
  raw_list = get_user_activity_list(user, act_type)
  result_list = []
  for act in raw_list:
    if int(act.year) == int(year):
      result_list.append(act)
      
  return result_list
  
def get_full_activity_list(act_type):
  if act_type == publication_type:
    return Activity.objects.all()
  elif act_type == conference_type:
    return Conference.objects.all()
  elif act_type == patent_type:
    return Patent.objects.all()
  elif act_type == monograph_type:
    return Monograph.objects.all()
  elif act_type == course_type:
    return Course.objects.all()
  elif act_type == supervising_type:
    return Supervising.objects.all()
  elif act_type == editing_type:
    return Editing.objects.all()
  elif act_type == editing_collegium_type:
    return EditingCollegium.objects.all()
  elif act_type == orgwork_type:
    return OrgWork.objects.all()
  elif act_type == opposing_type:
    return Opposing.objects.all()
  elif act_type == grant_type:
    return Grant.objects.all()
  elif act_type == award_type:
    return Award.objects.all()
  
def get_total_num_and_cost(act_type, act_list):
  num = 0
  cost = 0
  for act in act_list:
    num += 1
    cost += get_activity_cost(act_type, act)
  return {'num': num, 'cost': cost}


