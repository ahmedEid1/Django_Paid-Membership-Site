from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login
import stripe

from plans.models import FitnessPlan, Customer
from .forms import CustomSignUp

# secret
stripe.api_key = 'sk_test_51HPUBcB5LDdfWvGkjQvngmIb9QXhjOHJAgHdm56XRONgln7dWnCtXCBOkXpOLgF1OvROroUaTVbNCWBJKvks99gx00xSwocwkS'


# Create your views here.

# updating our customer plans
@user_passes_test(lambda u: u.is_superuser)
def updateaccounts(request):
    customers = Customer.objects.all()
    for customer in customers:
        subscription = stripe.Subscription.retrieve(customer.stripe_subscription_id)
        if subscription.status != 'active':
            customer.membership = False
        customer.membership = True

        # in case we update it in stripe account mby hand
        customer.cancel_at_period_end = subscription.cancel_at_period_end
        customer.save()
    return HttpResponse("update completed ")



def home(request):
    plans = FitnessPlan.objects.all()
    return render(request, 'plans/home.html',
                  {'plans': plans})


def plan(request, plan_id):
    the_plan = get_object_or_404(FitnessPlan, pk=plan_id)
    if the_plan.premium:
        if request.user.is_authenticated:
            try:
                if request.user.customer.membership:
                    return render(request, 'plans/plan.html',
                                  {'plan': the_plan})
            except Customer.DoesNotExist:
                return redirect('join')

        return redirect('join')
    return render(request, 'plans/plan.html',
                  {'plan': the_plan})


def join(request):
    return render(request, 'plans/join.html')


@login_required
def checkout(request):
    try:
        if request.user.customer.membership:
            return redirect('settings')
    except Customer.DoesNotExist:
        pass

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
        customer = Customer()
        customer.user = request.user
        customer.stripe_id = stripe_customer.id
        customer.membership = True
        customer.cancel_at_period_end = False
        customer.stripe_subscription_id = subscription.id
        customer.save()

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


@login_required()
def settings(request):
    membership = False
    cancel_at_period_end = False

    if request.method == 'POST':
        subscription = stripe.Subscription.retrieve(request.user.customer.stripe_subscription_id)
        subscription.cancel_at_period_end = True

        request.user.customer.cancel_at_period_end = True
        cancel_at_period_end = True

        subscription.save()
        request.user.customer.save()
    else:
        try:
            if request.user.customer.membership:
                membership = True
            if request.user.customer.cancel_at_period_end:
                cancel_at_period_end = True
        except Customer.DoesNotExist:
            membership = False

    return render(request, 'registration/settings.html',
                  {'membership': membership, 'cancel_at_period_end': cancel_at_period_end})


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

