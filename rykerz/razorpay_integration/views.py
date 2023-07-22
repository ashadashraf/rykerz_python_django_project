from django.shortcuts import render, redirect
from .models import RazorpayOrder
from django.views.decorators.csrf import csrf_exempt
import razorpay
from rykerz.settings import (RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET,)
from .constants import PaymentStatus
import json
from django.urls import reverse
from authentication.models import CustomUser
from urllib.parse import quote
from userside.models import InstantBuy, Product, Order, BulkOrder, Cart, Transaction
from django.contrib import messages
from datetime import datetime
from django.db.models import Avg


# Create your views here.

# def razorpay_home(request):
#     print('razorpay')
#     return render(request, "razorpay_integration/index.html")

def order_payment(request, id, amount, bulk_order):
    amount = float(amount)
    amount = int(amount)
    if request.user.is_authenticated:
        customer = CustomUser.objects.get(id=id)
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create(
            {"amount": amount * 100, "currency": "INR", "payment_capture": "1"}
        )
        order = RazorpayOrder.objects.create(
            name=customer.name, amount=amount, provider_order_id=razorpay_order["id"]
        )
        order.save()

        user = customer.id
        bulk_number = bulk_order.bulk_order
        # Encode the values
        encoded_customer = quote(str(user).encode('utf-8'))
        encoded_amount = quote(str(amount).encode('utf-8'))
        encoded_bulk_order = quote(str(bulk_number).encode('utf-8'))
        callback_url = f"http://127.0.0.1:8000/callback/{encoded_customer}/{encoded_amount}/{encoded_bulk_order}"
        return render(
            request,
            "razorpay_integration/payment.html",
            {
                "callback_url":  callback_url,
                "razorpay_key": RAZORPAY_KEY_ID,
                "order": order,
            },
        )
    return render(request, "razorpay_integration/payment.html")


@csrf_exempt
def callback(request, customer, amount, bulkorder):
    print(customer, amount, bulkorder)
    customer = CustomUser.objects.get(id=customer)
    bulk_order = BulkOrder.objects.get(bulk_order=bulkorder)
    def verify_signature(response_data):
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        return client.utility.verify_payment_signature(response_data)

    if "razorpay_signature" in request.POST:
        payment_id = request.POST.get("razorpay_payment_id", "")
        provider_order_id = request.POST.get("razorpay_order_id", "")
        signature_id = request.POST.get("razorpay_signature", "")
        rp_order = RazorpayOrder.objects.get(provider_order_id=provider_order_id)
        rp_order.payment_id = payment_id
        rp_order.signature_id = signature_id
        rp_order.save()

        if verify_signature(request.POST):
            rp_order.status = PaymentStatus.SUCCESS
            rp_order.save()

            if InstantBuy.objects.filter(customer = customer, selected=True):
                instantbuy = InstantBuy.objects.filter(selected=True)
                for item in instantbuy:
                    product = Product.objects.get(id=item.product.id)
                    if item.quantity <= product.stock:
                        product.stock -= item.quantity
                        if product.offer_price:
                            total_amount = product.offer_price*item.quantity
                            unit_price = product.offer_price
                        else:
                            total_amount = product.sales_price*item.quantity
                            unit_price = product.sales_price
                        order = Order(customer=customer, product=product, quantity=item.quantity, order_status='requesting', payment_status=True, amount=unit_price, total_amount=total_amount, bulk_order=bulk_order)
                        order.save()
                        product.save()
                    else:
                        messages.success(request, '{{product.product_name}} is out of stock')
                average_tax_amount = Order.objects.filter(bulk_order=bulk_order).aggregate(Avg('tax_amount'))['tax_amount__avg']
                InstantBuy.objects.all().delete()
            else:
                cart_items = Cart.objects.filter(customer=customer, selected=True)
                for item in cart_items:
                    product = Product.objects.get(id=item.product.id)
                    if item.quantity <= product.stock:
                        product.stock -= item.quantity
                        if product.offer_price:
                            total_amount = product.offer_price*item.quantity
                            unit_price = product.offer_price
                        else:
                            total_amount = product.sales_price*item.quantity
                            unit_price = product.sales_price
                        order = Order(customer=customer, product=product, quantity=item.quantity, order_status='requesting', payment_status=True, amount=unit_price, total_amount=total_amount, bulk_order=bulk_order)
                        order.save()
                        product.save()
                        Cart.objects.filter(customer=customer, selected=True, product=item.product.id).delete()
                    else:
                        messages.success(request, '{{product.product_name}} is out of stock')
                average_tax_amount = Order.objects.filter(bulk_order=bulk_order).aggregate(Avg('tax_amount'))['tax_amount__avg']
            bulk_order.payment_status = True
            bulk_order.tax_amount = average_tax_amount
            bulk_order.save()
            transaction = Transaction(bulk_order=bulk_order, transaction_mode='razorpay', payment_gateway_id=rp_order.payment_id, transaction_amount=bulk_order.final_amount, transaction_date=datetime.now(), transaction_status=PaymentStatus.SUCCESS)
            transaction.save()
            # try:
            #     address = customer.address_set.get(id=customer.id, active_address=True)
            #     return render(request, "razorpay_integration/callback.html", context={"status": rp_order.status, "bulk_order": bulk_order})
            # except:
            #     return redirect('home', request.user.id)
            return render(request, "razorpay_integration/callback.html", context={"status": rp_order.status, "bulk_order": bulk_order, "customer":customer})
        else:
            rp_order.status = PaymentStatus.FAILURE
            rp_order.save()
            bulk_order.delete()
            try:
                return render(request, "razorpay_integration/callback.html", context={"status": rp_order.status, "bulk_order": bulk_order, "customer":customer})
            except:
                return redirect('home', request.user.id)
    else:
        try:
            payment_id = json.loads(request.POST.get("error[metadata]")).get("payment_id")
            provider_order_id = json.loads(request.POST.get("error[metadata]")).get("order_id")
            rp_order = RazorpayOrder.objects.get(provider_order_id=provider_order_id)
            rp_order.payment_id = payment_id
            rp_order.status = PaymentStatus.FAILURE
            rp_order.save()
            bulk_order.delete()
            return render(request, "razorpay_integration/callback.html", context={"status": rp_order.status, "bulk_order": bulk_order, "customer":customer})
        except:
            return redirect('home', request.user.id)