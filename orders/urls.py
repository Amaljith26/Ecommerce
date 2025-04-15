from django.urls import path
from . import views

urlpatterns = [
    path('order-history/', views.order_history, name='order_history'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    
]
