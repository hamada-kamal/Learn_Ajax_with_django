from django.db import models
from django.db.models.fields.related import ForeignKey
from django.http import response
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# from django.core.urlresolvers import reverse
# Create your models here.



class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200)

    def __str__(self):
        return str(self.user)

def create_customer(sender , **kwargs):
    if kwargs['created']:
        user_profile = Customer.objects.create(user=kwargs['instance'])
        
post_save.connect(create_customer , sender=User)


from django.contrib.auth.signals import user_logged_in
import json
from django.shortcuts import redirect, render
from django.http.response import HttpResponse





def do_stuff(sender, user, request, **kwargs):
    print("user from models signal: ",user)
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

        


user_logged_in.connect(do_stuff)



class Product(models.Model):
    name = models.CharField(max_length=100 , verbose_name=_("Product Name "))
    image = models.ImageField(upload_to='prodcut/' , verbose_name=_("Image") , blank=True, null=True)
    price = models.DecimalField(max_digits=7  , decimal_places=2 , verbose_name=_("Price"))
    digital = models.BooleanField(default=False,null=True, blank=True)
    like = models.ManyToManyField(Customer,blank=True)
    PRDSLug = models.SlugField(blank=True, null=True , verbose_name=_("slug"))



    def save(self , *args  ,**kwargs ):
        self.PRDSLug = slugify(self.name)
        super(Product , self).save( *args , **kwargs)



    @property
    def likeNumber(self):
        return self.like.all().count()
    def imageURL(self):
        try:
            url=self.image.url
        except:
            url=''
        return url    


    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.PRDSLug})

    def __str__(self):
        return self.name





class ProductImage(models.Model):
    PRDIProduct = models.ForeignKey(Product , on_delete=models.CASCADE , verbose_name=_("Product"))
    PRDIImage = models.ImageField(upload_to='prodcut/' , verbose_name=_("Image"))

    def __str__(self):
        return str(self.PRDIProduct)





class Order(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True)
    


    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for i in orderitems:
    	    if i.product.digital == False:
             shipping = True
        return shipping
   

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total 

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total 

    def __str__(self):
	    return "Order Name: " +str(self.customer)
    




class OrderItem(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total
    def __str__(self):
	    return str(self.product)


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
    	return self.address