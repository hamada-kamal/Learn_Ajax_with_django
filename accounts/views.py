from django.http import response
from django.shortcuts import render , redirect , get_object_or_404
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth import login 
from .models import Profile
# from .forms import UserForm , ProfileForm
from django.contrib.auth.decorators import login_required
from product.models import Order

from django.contrib.auth import logout








from django.urls import reverse


def logout_view(request):
    print("************log out*************")
    response = redirect(reverse('products:store'))
    response.delete_cookie("cart")
    logout(request)
    return response
 
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/products')

    else:
        form = UserCreationForm()

    context = {'form' : form}
    return render(request , 'registration/signup.html' , context)


@login_required(login_url='/accounts/login/')
def profile(request , slug):

    profile = get_object_or_404(Profile , slug=slug)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.get_cart_items
    else:
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping': False}  
        cartItems = order['get_cart_items']
    context = {'profile' : profile,'cartItems': cartItems}
    return render(request , 'profile.html' , context)