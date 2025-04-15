from django.shortcuts import render,get_object_or_404
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth.models import User
from .models import Order, OrderItem
from cart.models import Cart
from decimal import Decimal
from django.conf import settings
from cart.models import Cart,CartItem
from django.core.paginator import Paginator


def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    # Set up pagination
    paginator = Paginator(orders, 5)  # Show 5 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'order_history.html', {'orders': page_obj})



def create_order(request):
    cart_items = CartItem.objects.filter(cart__user=request.user)  

    if not cart_items.exists():
        print("No items in the cart.")
        return None  

    order = Order.objects.create(user=request.user, total_price=Decimal('0.00'))  
    total_price = Decimal('0.00') 

    for item in cart_items:
        product = item.product
        quantity = item.quantity
        price = product.price
        item_total_price = price * quantity 

        print(f"Product: {product.name}, Quantity: {quantity}, Price: {price}, Item Total Price: {item_total_price}")

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=item_total_price
        )

        total_price += item_total_price  
    order.total_price = total_price
    order.save()

    return order

  

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_email = session.get('customer_email')

        try:
            user = User.objects.get(email=customer_email)
            cart = Cart.objects.get(user=user)

            # ✅ Create order
            order = Order.objects.create(user=user, total_price=0)

            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                order.total_price += cart_item.product.price * cart_item.quantity

            order.save()

            cart.items.all().delete()

        except User.DoesNotExist:
            print("User not found.")
        except Cart.DoesNotExist:
            print("Cart not found.")

    return HttpResponse(status=200)

def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_detail.html', {'order': order})