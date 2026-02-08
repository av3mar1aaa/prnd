# This Python file uses the following encoding: utf-8
from django.core.exceptions import ObjectDoesNotExist
from prnd.calculator.models import YearStatistics, Attribute
from prnd.calculator.attributes import get_attribute

def get_user_yearstatistics(user,year):
  try:
    ys = user.yearstatistics_set.get(year=year)
  except ObjectDoesNotExist:
    return calculate_year_statistics(user, year)
  return ys

def calculate_coef_and_reason(user, year): 
    a = get_attribute(user)
    coef = 1.0
  
#    for i in range(0, a.rate):
#      coef_modifier = coef_modifier/ 2

#    if a.rate == 1:
#      coef = coef * 0.9
#    elif a.rate == 2:
#      coef = coef * 0.8
#    elif a.rate == 3: 
#      coef = coef * 0.75
#    elif a.rate == 4:
#      coef = coef * 0.7
#    elif a.rate == 5: 
#      coef = coef * 0.6
#    elif a.rate == 6:
#      coef = coef * 0.5
#    elif a.rate == 7: 
#      coef = coef * 0.4
#    elif a.rate == 8:
#      coef = coef * 0.3
#    elif a.rate == 9: 
#      coef = coef * 0.25
#    elif a.rate == 10:
#      coef = coef * 0.2
#    elif a.rate == 11: 
#      coef = coef * 0.1
#    reason = "%s (ставка = %s) " % (coef, coef)
# kulikov, 2011-01-27: код выше закомментирован, потому что на ставку 
# решили не домножать
    coef = 1.0
    reason = "1.0 "
    vishee = False
    
    if a.diplom_year != None:
      years_diff = year - a.diplom_year
    
      if years_diff  < 6 and years_diff > -1 :
        coef = coef * 2
        reason = reason + "* 2 (высшее образование получено менее пяти лет назад) "
        vishee = True

    if a.phd_year != None and ( (a.degree == 'K' and year - a.birth_year <= 40) or ( a.degree == 'D') ) and (vishee == False):
        years_diff = year - a.phd_year
      #if coef <= 1.0:
        if years_diff == 0:
          coef = coef * 2
          reason = reason + "* 2 (степень получена менее года назад) "
        elif year - a.phd_year < 3 and  years_diff >= 0:
          coef = coef * 1.5
          reason = reason + "* 1.5 (степень получена менее трех лет назад) "

#    if a.degree == 'D' and a.phd_year != None
#      years_diff = year - a.phd_year
#      if coef <= 1:
#        if years_diff < 2 and years_diff > 0:
#          coef = coef * 2
#          reason = reason + "* 2 (степень получена менее года назад) "
#        elif year - a.phd_year < 4 and  years_diff > 0:
#          coef = coef * 1.5
#          reason = reason + "* 1.5 (степень получена менее трех лет назад) "

    if a.status == 'S':
      coef = 0.0
      reason = "аспирант"
    elif  a.status == 'K': 
      coef = 0.0
      reason = "работа по контракту"

    if a.rank == 'N':
      coef = 0.0
      reason = "нет должности"
      
    return [coef, reason]
  
def calculate_year_statistics(user, year):
    coef_and_reason = calculate_coef_and_reason(user, year)

    ys = YearStatistics(user = user,
        year = year,
        reason = coef_and_reason[1],
        coef_modifier = coef_and_reason[0],
        status = 0,
        calcasmaximum = False,
        additional_coef = 0.0)
    ys.save()
    return ys
