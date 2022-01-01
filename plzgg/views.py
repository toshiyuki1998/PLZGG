# Create your views here.

from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UserForm
import plotly.graph_objects as go
import os

from .programs import config, database_tools

def index(request):
    return HttpResponse("<h1>Index</h1>") 
 
def plzgg(request):
    return render(request, "index.html")


def forms(request):
    params = {"summoner_name":"", "champion_name":"", "champion_position":""}
    if request.POST:
        form = UserForm(request.POST)
        if form.is_valid():
            params["summoner_name"] = request.POST["summoner_name"]
            params["champion_name"] = request.POST["champion_name"]
            params["champion_position"] = request.POST["champion_position"]
            params["fig"] = database_tools.get_data(params["summoner_name"], params["champion_name"], params["champion_position"])
            return render(request, "analyze.html", params)
    
    else:
        form = UserForm()
        params["form"] = form
        return render(request, "form.html", params)



