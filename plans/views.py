from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login

from plans.models import FitnessPlan
from .forms import CustomSignUp


# Create your views here.
def home(request):
    plans = FitnessPlan.objects.all()
    return render(request, 'plans/home.html',
                  {'plans': plans})


def plan(request, plan_id):
    the_plan = get_object_or_404(FitnessPlan, pk=plan_id)
    if the_plan.premium:
        return redirect('join')
    return render(request, 'plans/plan.html',
                  {'plan': the_plan})


def join(request):
    return render(request, 'plans/join.html')


def checkout(request):
    return render(request, 'plans/checkout.html')


def settings(request):
    return render(request, 'registration/settings.html')


class SignUp(generic.CreateView):
    form_class = CustomSignUp
    success_url = reverse_lazy('home')
    template_name = 'registration/signup.html'


    def form_valid(self, form):
        valid = super(SignUp, self).form_valid(form)

        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')

        new_user = authenticate(username=username, password=password)
        login(self.request, new_user)

        return valid

