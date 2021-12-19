from django.urls import path
from . import views


app_name = 'product'

urlpatterns = [
    
    path('',views.all_product , name='store'),
    path('autosearch',views.autoSearch , name='autosearch'),
    path( '<slug:slug>', views.product_detail , name='product_detail'),
    path('cart/',views.cart , name='cart'),
    
    # login to checkout
    # path('login-to-checkout/', views.checkout_login_page, name="checkout_login"),
    path('log-out/',views.logout_view , name='customLogout' ),

    # sign up to checkout
    # path('signup-to-checkout/', views.checkout_signup_page, name="checkout_signup"),
    # path('user-data/', views.get_login_data, name="login_data"),

    path('checkout/',views.checkout , name='checkout'),
    path('likeItem/', views.likeItem, name="likeItem"),
    path('favorites/', views.liked_product, name="liked_product"),
    path('process_order/', views.processOrder, name="process_order"),
    # ajax func urls
    path('addToCartWithAjax/', views.addToCartWithAjax, name="addToCartWithAjax"),
    path('cartInfo/', views.cartInfo, name="cartInfo"),
    
    
] 
