from django.shortcuts import render

from plans.models import FitnessPlan


# Create your views here.
def home(request):
    plans = FitnessPlan.objects.all()
    return render(request, 'plans/home.html',
                  {'plans': plans})
