from django.shortcuts import redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.contrib.auth.views import LoginView
from django.views.generic.edit import FormView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Task

import time
from plyer import notification
from threading import *
# Create your views here.

def mythread():
    while True:
        notification.notify(
            title = "Knock Knock!!!",
            message ="You may have some pending tasks in your Schedule.",
            timeout= 10
            )
        time.sleep(60*30)

t=Thread(target=mythread)
t.start()

class TaskList(LoginRequiredMixin,ListView):
    model=Task
    context_object_name = 'Task'

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['Task']=context["Task"].filter(user=self.request.user)
        context['count']=context['Task'].filter(complete=False).count()
        search_input=self.request.GET.get('Search-Area') or ''                         #search button
        if search_input:
            context['Task']=context['Task'].filter(title__icontains=search_input)   #title__startswith-->searches whole string
            context[search_input]=search_input
        return context


class TaskDetail(LoginRequiredMixin,DetailView):
    model=Task
    context_object_name = 'Task'
    template_name='todo/task.html'


class TaskCreate(LoginRequiredMixin,CreateView):
    model=Task
    fields=['title','description','complete']
    success_url= reverse_lazy('Task')

    def form_valid(self,form):
        form.instance.user=self.request.user
        return super(TaskCreate,self).form_valid(form)

class TaskUpdate(LoginRequiredMixin,UpdateView):
    model=Task
    fields=['title','description','complete']
    success_url=reverse_lazy('Task')

class TaskDelete(LoginRequiredMixin,DeleteView):
    model=Task
    context_object_name = 'task'
    success_url = reverse_lazy('Task')

class CustomLoginView(LoginView):
    template_name = 'todo/login.html'
    fields="__all__"
    redirect_authenticated_user = False

    def get_success_url(self):
        return reverse_lazy('Task')

class RegisterPage(FormView):
    template_name = 'todo/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user=True
    success_url = reverse_lazy('Task')

    def form_valid(self,form):                #when user will register,they will be automatically logged in instead of going to the login page
        user=form.save()
        if user is not None:
            login(self.request,user)
        return super(RegisterPage,self).form_valid(form)

    def get(self,*args,**kwargs):                 #user was able to access register page from link option..to stop that this code is used
        if self.request.user.is_authenticated:
            return redirect('Task')
        return super(RegisterPage,self).get(*args,**kwargs)


