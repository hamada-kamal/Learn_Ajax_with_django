import json
from .models import *


def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart={}
    
    order = {'get_cart_total':0, 'get_cart_items':0, 'shipping': False}
    cartItems = order['get_cart_items']
    
    items = []
    for i in cart:
        try:
            cartItems += cart[i]['quantity']
            product = Product.objects.get(id = i)
            total = (product.price * cart[i]['quantity'])
            order['get_cart_total'] +=total 
            order['get_cart_items'] +=cart[i]['quantity']
            item = {
                'product':{
                    'id':product.id,
                    'name':product.name,
                    'price':product.price,
                    'imageURL':product.imageURL,
                    'PRDSLug':product.PRDSLug,
                },
                'quantity':cart[i]['quantity'],
                'get_total': total,
            }
            items.append(item)
            if product.digital ==False:
                order['shipping']=True
        except:
            pass 

    return {'cartItems': cartItems, 'order': order, 'items':items}


def CartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']

    return {'cartItems': cartItems, 'order': order, 'items':items}

def guestOrder(request, data):
    print("user not loged in ..")
    print("COOKIES", request.COOKIES)
    name = data['form']['name']
    email = data['form']['email']
    cookieData = cookieCart(request)
    items = cookieData['items']
    customer, created = Customer.objects.get_or_create(
        email = email,
    )
    customer.name = name
    customer.save()
    order = Order.objects.create(
        customer = customer,
        complete = False,
    )
    for item in items:
        product = Product.objects.get(id = item['product']['id'])
        orderItem = OrderItem.objects.create(
            product = product,
            order = order,
            quantity = item['quantity']
        )
    if order.shipping == True:
        ShippingAddress.objects.create(
        customer=customer,
        order=order,
        address=data['shipping']['address'],
        city=data['shipping']['city'],
        state=data['shipping']['state'],
        zipcode=data['shipping']['zipcode'],
        )
    return customer, order    