from django.contrib.admin import widgets
from django import forms
from models import Item
import datetime

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        exclude = ('user',) # Don't let the user choose who this item belongs to
        
    def clean_due(self):
        date = self.cleaned_data['due']
        if date == None: # We allow no date
            return date
        if date < datetime.date.today(): # But not a wrong date
            raise forms.ValidationError("The date cannot be in the past!")
        return date