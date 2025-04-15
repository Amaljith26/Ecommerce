from django.urls import path
from . import views

app_name = 'cart'
urlpatterns = [
    path('', views.cart_view, name='cart_view'),  
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('update-quantity/', views.update_quantity, name='update_quantity'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
   
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('success/', views.success, name='success'),
    

    
]

