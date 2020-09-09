from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login
import stripe

from plans.models import FitnessPlan
from .forms import CustomSignUp

# secret
stripe.api_key = 'sk_test_51HPUBcB5LDdfWvGkjQvngmIb9QXhjOHJAgHdm56XRONgln7dWnCtXCBOkXpOLgF1OvROroUaTVbNCWBJKvks99gx00xSwocwkS'


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


@login_required
def checkout(request):
    coupons = {'friend': 5, 'brother': 6, 'me': 90}

    if request.method == 'POST':
        stripe_customer = stripe.Customer.create(email=request.user.email,
                                                 source=request.POST['stripeToken'])
        plan = 'price_1HPUMpB5LDdfWvGkZZzzR2X9'
        if request.POST['plan'] == 'yearly':
            plan = 'price_1HPUNoB5LDdfWvGksEeI9ie9'

        if request.POST['coupon'] in coupons:
            coupon = request.POST['coupon'].lower()
            percentage = coupons[coupon]
            try:
                coupon = stripe.Coupon.create(duration='once',
                                     id=request.POST['coupon'].lower(), percent_off=percentage)
            except:
                pass

            subscription = stripe.Subscription.create(customer=stripe_customer.id,
                                                      items=[{'plan': plan}], coupon=request.POST['coupon'].lower())

        else:
            subscription = stripe.Subscription.create(customer=stripe_customer.id,
                                                      items=[{'plan': plan}])

        return redirect('home')
    plan = "yearly"
    coupon = 'none'
    price = 100000
    og_dollar = 100
    coupon_dollar = 0
    final_dollar = 100
    if request.method == "GET" and 'plan' in request.GET:
        if request.GET['plan'] == 'monthly':
            plan = "monthly"
            coupon = 'none'
            price = 10000
            og_dollar = 10
            coupon_dollar = 0
            final_dollar = 10

    if request.method == "GET" and 'coupon' in request.GET:
        if request.GET['coupon'].lower() in coupons:
            # update the coupon
            coupon = request.GET['coupon'].lower()

            percentage = coupons[coupon]
            coupon_price = int(percentage / 100 * price)
            # update price and coupon amount
            price -= coupon_price
            coupon_dollar = str(coupon_price)[:-2] + '.' + str(coupon_price)[-2:]
            final_dollar = str(price)[:-2] + '.' + str(price)[-2:]

    return render(request, 'plans/checkout.html',
                  {"plan": plan, 'coupon': coupon, 'price': price, 'og_dollar': og_dollar,
                   'coupon_dollar': coupon_dollar, 'final_dollar': final_dollar})


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
