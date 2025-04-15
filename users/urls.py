from django.urls import path
from . import views

urlpatterns = [
    path('Sign In/', views.Signuppage, name='signup'),
    path('Login/', views.Loginpage, name='login'),
    path('Logout/',views.Logoutpage, name='logout'),
    
]