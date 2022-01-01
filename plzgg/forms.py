from django import forms
from .programs import config

class UserForm(forms.Form):
    summoner_name = forms.CharField(label='Summoner Name', max_length=100)
    champion_name = forms.CharField(label='Champion Name', max_length=100)
    champion_position = forms.CharField(label='Champion Position', max_length=100)





