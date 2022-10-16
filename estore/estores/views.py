import imp
from pickle import LIST
from re import template
import re
from tabnanny import check
from webbrowser import get
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect
from .forms import SignUpForm, CheckoutForm
from django.utils import timezone
from .models import Item, Order, OrderItem, BillingAddress



class HomeView(ListView):
    model = Item
    template_name = "home.html"

class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"

class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object' : order
            }
            return render(self.request, 'cart.html', context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect('estores:home')

class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        context = {
            'form': form
        }
        return render(self.request, "checkout.html", context)
    
    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country') 
                zip = form.cleaned_data.get('zip')
                state = form.cleaned_data.get('state')
                # same_shipping_address = form.cleaned_data.get('same_shipping_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip,
                    state=state
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                return redirect('estores:checkout')
            messages.warning(self.request, "Failed checkout")
            return redirect('estores:checkout')
            
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect('estores:home')

class PaymentView(View):
    def get(self, *args, **kwargs):
        return render(self.request, "payment.html")
        

@login_required(login_url='estores:login')
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
        )
    order_qs = Order.objects.filter(user=request.user,  ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("estores:product", slug=slug)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
    return redirect("estores:product", slug=slug)

@login_required(login_url='estores:login')
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user,  ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
                )[0]
            order.items.remove(order_item)
            messages.info(request, "This item was removed from your cart.")
            return redirect("estores:order-summary")
        else:
            messages.info(request, "This item was not in your cart.")
            return redirect("estores:order-summary")
    else:
        messages.info(request, "You do not have an active order.")
        return redirect("estores:order-summary")

@login_required(login_url='estores:login')
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user,  ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
                )[0]
            if order_item.quantity > 1:
                order_item.quantity -=1
                order_item.save()
                messages.info(request, "This item quantity was updated.")
            else:
                order.items.remove(order_item)
                messages.info(request, "This item was removed from cart")
            return redirect("estores:order-summary")

        else:
            messages.info(request, "This item was not in your cart.")
            return redirect("estores:home")
    else:
        messages.info(request, "You do not have an active order.")
        return redirect("estores:home")

@login_required(login_url='estores:login')
def add_single_item_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user,  ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
                )[0]
            order_item.quantity +=1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("estores:order-summary")
        else:
            messages.info(request, "This item was not in your cart.")
            return redirect("estores:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order.")
        return redirect("estores:product", slug=slug)

def signup(request):
    if request.user.is_authenticated:
        return redirect('estores:home')
    else:
        form = SignUpForm()
        if request.method == 'POST':
            form = SignUpForm(request.POST)
            if form.is_valid():
                form.save()
                
                username = form.cleaned_data.get("username")
                email = form.cleaned_data.get("email")
                password1 = form.cleaned_data.get("password1")
                password2 = form.cleaned_data.get("password2")
                new_user = authenticate(username=username, email=email, password=password1, password2 = password2)
                if new_user is not None:
                    login(request, new_user)
                    messages.success(request,   'Account created for '+ username )
                return redirect('estores:home')
        
        context = {
            'form': form
        }
        return render(request, 'login.html', context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('estores:home')
    else:
        if request.method == 'POST' and 'login' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('estores:home')
            else:
                messages.info(request, 'Username OR password is incorrect')
        context = {}
        return render(request, 'login.html', context)

def logoutUser(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('estores:login')
    else:
        return redirect('estores:login')
