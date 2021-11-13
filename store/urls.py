from django.urls import path
from . import views



urlpatterns=[
    path('',views.user_login,name="login"),
    path('logout/',views.userlogout,name="logout"),
    path('store/',views.store,name="store"),
    path('cart/',views.cart,name="cart"),
    path('checkout/',views.checkout,name="checkout"),
    path('signup/',views.signup,name='signup'),
    path('update_item/',views.updateItem,name='update_item'),
    path('process_order/',views.processOrder,name='process_order'),
]