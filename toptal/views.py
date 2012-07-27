from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.views import login

def home_page(request):
    """Display the home page, if not logged in, or redirect to the todo app if logged in"""
    if request.user.is_authenticated():
        return HttpResponseRedirect('/todo/')
    else:
        return render_to_response('index.html', context_instance=RequestContext(request))
        
def login_user(request, **kwargs):
    """Show user the login page if not logged in, or redirect to the todo app if logged in"""
    if request.user.is_authenticated():
        return HttpResponseRedirect('/todo/')
    else:
        return login(request, **kwargs)
    
def logout_user(request):
    """Log users out and redirect them to the home page"""
    logout(request)
    return HttpResponseRedirect('/')
    
def register_user(request):
    """Display a registration form and register a new user account if filled out properly"""
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST.copy())
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/login/")
    else:
        form = UserCreationForm()

    return render_to_response("registration/register.html", {
        'form' : form, 
    },context_instance=RequestContext(request))
    
def change_settings(request):
    """Allow authenticated users to change their settings"""
    if request.user.is_authenticated():
        return render_to_response('settings.html', context_instance=RequestContext(request))
    return HttpResponseRedirect('/')