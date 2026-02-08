import datetime
from prnd.calculator.models import Attribute
from django.core.exceptions import ObjectDoesNotExist

def get_attribute(user):
  try:
    a = user.attribute
  except ObjectDoesNotExist:
    cur_year = datetime.date.today().year
    a = Attribute(rate=0,
        rank = 'N',
        status = 'N',
        title = 'N',
        phd_year = cur_year,
        degree = 'N',
        user = user)
    a.save()
  return a
  

