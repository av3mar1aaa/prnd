# This Python file uses the following encoding: utf-8
import re
from prnd.legacy import validators
from prnd.legacy import forms
from prnd.calculator.models import SelectedJournal

class addSelectedJournalList(forms.Manipulator):
  def __init__(self):
    self.fields = (
    forms.LargeTextField(field_name='list',
      is_required=True, rows=20, cols=60, 
      ),
    )

  def getList(self, data):
    patern = re.compile('.+')
    list = patern.findall(data['list'])
    return list
    

class SelectedJournalForm(forms.Manipulator):
  def __init__(self):
    self.fields = (
    forms.TextField(field_name='fullname',
      length=30, maxlength=500,
      is_required=True, 
      ),
    forms.SelectField(field_name='type',
      choices=[s for s in SelectedJournal.TYPE_CHOICES],
      ),
    forms.FloatField(field_name='impactfactor',max_digits=8,decimal_places=3)
    )
    
  def form2object(self, form_data): 
    j =  SelectedJournal(
        fullname  = form_data['fullname'],
        type      = form_data['type'],
        impactfactor = form_data['impactfactor'],
        )
    return j

