from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from cart.models import Cart, CartItem
from store.models import Product
import json
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import stripe
from django.conf import settings
from orders.views import create_order
import os


def index(request):
    return render(request, 'index.html')


@login_required(login_url='login')
def cart_view(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        cart_subtotal = sum(item.product.price * item.quantity for item in cart_items)
        cart_total = cart_subtotal  

        return render(request, 'cart.html', {
            'cart_items': cart_items,
            'cart_subtotal': cart_subtotal,
            'cart_total': cart_total,
            'empty_cart': not cart_items.exists(),
            'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY
        })

    except Cart.DoesNotExist:
        return render(request, 'cart.html', {
            'cart_items': [],
            'cart_subtotal': 0,
            'cart_total': 0,
            'empty_cart': True,
            'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY
        })


@csrf_protect
@login_required
def add_to_cart(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            product_id = data.get("product_id")
            quantity = int(data.get("quantity", 1))

            if not product_id:
                return JsonResponse({"message": "Product ID is required"}, status=400)

            product = Product.objects.get(id=product_id)
            cart, _ = Cart.objects.get_or_create(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            if not created:
                cart_item.quantity += quantity
            else:
                cart_item.quantity = quantity
            cart_item.save()

            return JsonResponse({"message": "Product added to cart"})

        except Product.DoesNotExist:
            return JsonResponse({"message": "Product not found"}, status=404)
        except Exception as e:
            print("Error adding to cart:", str(e))
            return JsonResponse({"message": str(e)}, status=500)
    return JsonResponse({"message": "Invalid request method"}, status=405)


def remove_from_cart(request, product_id):
    try:       
        product = get_object_or_404(Product, id=product_id) 
        cart = Cart.objects.get(user=request.user)
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.delete()
        return redirect('cart:cart_view')
    except Cart.DoesNotExist:
        return redirect('cart:cart_view')
    
    except CartItem.DoesNotExist: 
        return redirect('cart:cart_view')
    

@csrf_exempt
@login_required
def update_quantity(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Received data:", data)  
            product_id = data.get('product_id')
            action = data.get('action')
            user = request.user
            print("Product ID:", product_id, "Action:", action)

            
            cart = Cart.objects.get(user=user) 
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id) 

            if action == 'increase':
                cart_item.quantity += 1
            elif action == 'decrease' and cart_item.quantity > 1:
                cart_item.quantity -= 1
            cart_item.save()
            cart_items = CartItem.objects.filter(cart=cart)  
            subtotal = sum(item.total_price() for item in cart_items)
            total = subtotal

            return JsonResponse({
                'success': True,
                'new_quantity': cart_item.quantity,
                'cart_subtotal': subtotal,
                'cart_total': total
            })

        except Cart.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Cart not found'}, status=404)
        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Cart item not found'}, status=404)
        except Exception as e:
            print("ERROR:", e)
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)



stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@csrf_exempt
@login_required
def create_checkout_session(request):
    if request.method == 'POST':
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)
            total = sum(item.total_price() for item in cart_items)
            amount_in_paise = int(total * 100)

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'inr',
                        'product_data': {
                            'name': 'Your Cart Total',
                        },
                        'unit_amount': amount_in_paise,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/cart/success/'),
                cancel_url=request.build_absolute_uri('/cart/cancel/'),
                
            )
            return JsonResponse({'id': session.id})
        except Exception as e:
            return JsonResponse({'error': str(e)})

def success(request):
    order = create_order(request)
    order.status = 'Completed'
    order.save()
    return render(request, 'success.html')