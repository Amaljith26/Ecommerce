from django.shortcuts import render,redirect
from django.shortcuts import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout


def Signuppage(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Validate passwords
        if password1 != password2:
            messages.error(request, "Passwords do not match!")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
        else:    
            user = User.objects.create_user(username=username, password=password1, email=email)
            user.first_name = name
            user.save()
            messages.success(request, "Account created successfully!")
            return redirect('login')

    return render(request, 'signup.html')



def Loginpage(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect('home') 
        else:
            messages.error(request, "Invalid username or password!")
    return render(request, 'login.html')

def Logoutpage(request):
    logout(request)
    return redirect('home')

