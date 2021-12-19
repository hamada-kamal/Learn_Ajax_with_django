# from django.http.response import HttpResponse
# from django.http.response import HttpResponse, HttpResponseRedirect
from django.http.response import HttpResponse
from django.shortcuts import render , get_object_or_404, redirect
from .models import Product, Order, OrderItem, ShippingAddress
from django.core.paginator import Paginator
from django.http import JsonResponse
import json
import datetime
from .utils import CartData
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth import login, logout
from .forms import LoginForm




def logout_view(request):
    print("************log out*************")
    response = redirect(reverse('products:store'))
    response.delete_cookie("cart")
    logout(request)
    return response
    
def all_product(request):
    search_qs = request.GET.get('searchname', '')
    if search_qs:
        products = Product.objects.filter(name__icontains=search_qs)
    else:
        products = Product.objects.all()

    paginator = Paginator(products, 100) 
    pages = request.GET.get('page')
    products = paginator.get_page(pages)

    data = CartData(request)
    cartItems = data['cartItems']
    context = {'products' : products, 'cartItems': cartItems,}
    return render(request , 'product/store.html' , context)




def product_detail(request , slug):
    product = get_object_or_404(Product ,PRDSLug=slug )
    data = CartData(request)
    cartItems = data['cartItems']

    context = {'product' : product, 'cartItems': cartItems,}
    return render(request , 'product/detail.html' , context)




def cart(request):
    data = CartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    # if request.user.is_authenticated:
    #     customer = request.user.customer
    #     order, created = Order.objects.get_or_create(customer=customer, complete=False)
    #     items = order.orderitem_set.all()
    #     cartItems = order.get_cart_items
    # else:
    #     mycart = json.loads(request.COOKIES['cart'])
    #     order = {'get_cart_total':0, 'get_cart_items':0, 'shipping': False}
    #     cartItems = order['get_cart_items']
    #     items = []
    #     for i in mycart:
    #         try:
    #             cartItems += mycart[i]['quantity']
    #             product = Product.objects.get(id = i)
    #             total = (product.price * mycart[i]['quantity'])
    #             order['get_cart_total'] +=total 
    #             order['get_cart_items'] +=mycart[i]['quantity']
    #             item = {
    #                 'product':{
    #                     'id':product.id,
    #                     'name':product.name,
    #                     'price':product.price,
    #                     'imageURL':product.imageURL,
    #                     'PRDSLug':product.PRDSLug,
    #                 },
    #                 'quantity':mycart[i]['quantity'],
    #                 'get_total': total,
    #             }
    #             items.append(item)
    #             if product.digital ==False:
    #                 order['shipping']=True
    #         except:
    #             pass
        
    return render(request, 'product/cart.html', {'items':items, 'order': order, 'cartItems': cartItems})
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate

 
def checkout_signup_page(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            if user:
                order, created = Order.objects.get_or_create(customer=user.customer, complete=False)
                cart = json.loads(request.COOKIES['cart'])
                if cart:
                    for line in cart:
                        product = Product.objects.get(id = line)
                        # check if the product in the user order's line or not
                        found = OrderItem.objects.filter(order=order, product=product).count()
                        if found:
                            orderitem = OrderItem.objects.get(order=order, product=product)
                            orderitem.quantity += cart[line]["quantity"]
                            orderitem.save()
                        else:
                            orderitem = OrderItem.objects.create(order=order, product=product)
                            orderitem.quantity = cart[line]["quantity"]
                            orderitem.save()

            login(request, user)   
            response = redirect(reverse('products:store'))
            response.delete_cookie("cart")
            return response

    else:
        form = UserCreationForm()

    context = {'form' : form}
    return render(request , 'product/check_signup.html' , context)


def checkout_login_page(request):
    form = LoginForm(request.POST or None)
    if request.POST and form.is_valid():
        #check_login return ==> user
        user = form.check_login(request)
        if user:
            order, created = Order.objects.get_or_create(customer=user.customer, complete=False)
            cart = json.loads(request.COOKIES['cart'])
            if cart:
                for line in cart:
                    product = Product.objects.get(id = line)
                    # check if the product in the user order's line or not
                    found = OrderItem.objects.filter(order=order, product=product).count()
                    if found:
                        orderitem = OrderItem.objects.get(order=order, product=product)
                        orderitem.quantity += cart[line]["quantity"]
                        orderitem.save()
                    else:
                        orderitem = OrderItem.objects.create(order=order, product=product)
                        orderitem.quantity = cart[line]["quantity"]
                        orderitem.save()

            login(request, user)
        
            response = redirect(reverse('products:store'))
            response.delete_cookie("cart")
            return response
    
    return render(request, 'product/check_login.html', {'login_form': form })


@login_required(login_url="/products/login-to-checkout/")
def checkout(request):
    data = CartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    return render(request, 'product/checkout.html', {'items':items, 'order': order, 'cartItems': cartItems})



def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    customer = request.user.customer
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    if order.shipping == True:
        ShippingAddress.objects.create(
        customer=customer,
        order=order,
        address=data['shipping']['address'],
        city=data['shipping']['city'],
        state=data['shipping']['state'],
        zipcode=data['shipping']['zipcode'],
        )

    order.complete = True
    order.save()    

    return JsonResponse('payment complete', safe=False)  
    


@login_required
def liked_product(request):
    customer = request.user.customer
    products = Product.objects.filter(like=customer)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    cartItems = order.get_cart_items

    return render(request, 'product/favorit.html', {'products':products, 'cartItems': cartItems})


def autoSearch(request):
    q_original = request.GET.get('term')
    qs = Product.objects.filter(name__icontains = q_original)
    if qs:
        names = []
        names+=[x.name for x in qs]
    else:
        names = ['No results']
    return JsonResponse(names, safe=False)


    
def addToCartWithAjax(request):
    if request.user.is_authenticated:
        product_id = request.GET.get("productId")
        action = request.GET.get("action")
        customer = request.user.customer
        product = Product.objects.get(id=product_id)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        objs_founded = OrderItem.objects.filter(order=order,product=product).count()
        if objs_founded:
            orderItem = OrderItem.objects.get(order=order,product=product)
            if action == "add":
                orderItem.quantity += 1
                orderItem.save()
            elif action == "remove" and orderItem.quantity > 1:
                orderItem.quantity -= 1
                orderItem.save()
            elif action == "delete":
                orderItem.delete()    
        else:
            orderItem = OrderItem.objects.create(order=order, product=product, quantity = 1)
            orderItem.save()
        data = {
        "cartQty": order.get_cart_items,  
            "productQty":orderItem.quantity,
            "line_price":orderItem.get_total,
            "cart_total":order.get_cart_total,
        }
    else:
        mycart = json.loads(request.COOKIES['cart'])
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping': False}
        cartItems = order['get_cart_items']
        items = []
        for i in mycart:
            try:
                cartItems += mycart[i]['quantity']
                product = Product.objects.get(id = i)
                total = (product.price * mycart[i]['quantity'])
                order['get_cart_total'] +=total 
                order['get_cart_items'] +=mycart[i]['quantity']
                item = {
                    'product':{
                        'id':int(product.id),
                        'name':f'{product.name}',
                        'price':float(product.price),
                        'imageURL':f'{product.imageURL}',
                        'PRDSLug':f'{product.PRDSLug}',
                    },
                    'quantity':int(mycart[i]['quantity']),
                    'get_total': int(total),
                }
                items.append(item)
                if product.digital ==False:
                    order['shipping']=True
            except:
                pass
        data = {
        "cartQty": order['get_cart_items'],  
        "items":json.dumps(items),
        "cart_total":order['get_cart_total'],
        } 
    return JsonResponse(data)


def likeItem(request):
    productId = request.GET.get("productId")
    product = Product.objects.get(id=productId)
    customer = request.user.customer
    if customer in product.like.all():
        product.like.remove(customer)
        added = False
    else:
        product.like.add(customer)
        added = True
    num_liked_products = Product.objects.filter(like=customer).count()

    data = {
        "added":added,
        "liked_num":product.likeNumber,
        "num_liked_products":num_liked_products,
    }
    print("num_liked_products: ",data["num_liked_products"])
    return JsonResponse(data)

def cartInfo(request):
    data = None
    if request.user.is_authenticated:
        customer = request.user.customer
        products = Product.objects.all()
        list = []
        for p in products:
            if customer in p.like.all():
                list.append(p.id)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        num_liked_products = Product.objects.filter(like=customer).count()
        data = {
        "cartQty": order.get_cart_items,  
        "cart_total": order.get_cart_total,
        "liked_list":list,
        "num_liked_products":num_liked_products,  
        }
    else:
        mycart = json.loads(request.COOKIES['cart'])
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping': False}
        cartItems = order['get_cart_items']
        items = []
        for i in mycart:
            try:
                cartItems += mycart[i]['quantity']
                product = Product.objects.get(id = i)
                total = (product.price * mycart[i]['quantity'])
                order['get_cart_total'] +=total 
                order['get_cart_items'] +=mycart[i]['quantity']
                item = {
                    'product':{
                        'id':int(product.id),
                        'name':f'{product.name}',
                        'price':float(product.price),
                        'imageURL':f'{product.imageURL}',
                        'PRDSLug':f'{product.PRDSLug}',
                    },
                    'quantity':int(mycart[i]['quantity']),
                    'get_total': int(total),
                }
                items.append(item)
                if product.digital ==False:
                    order['shipping']=True
            except:
                pass
        
        data = {
        "cartQty": order['get_cart_items'],  
        "items":json.dumps(items),
        "cart_total":order['get_cart_total'],
        #"liked_list":[],
        } 

    return JsonResponse(data, safe=False)


