from django.shortcuts import render
from .models import Product
# Create your views here.

def Home(request):
    products = Product.objects.all()  # Get all products
    chunked_products = [products[i:i + 4] for i in range(0, len(products), 4)]
    return render(request, 'index.html', {'chunked_products': chunked_products})