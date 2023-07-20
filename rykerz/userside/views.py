from django.shortcuts import render, redirect
from adminside.models import Product, Category, SubCategory, ProductImage
from authentication.models import CustomUser
from userside.models import Cart, Address, Order, Transaction, Coupon, BulkOrder, InstantBuy, Favourites, Wallet
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from authentication.decorators import verification_required
from django.views.decorators.cache import never_cache
from django.db.models import Sum, Avg, Q
from django.http import HttpResponse
from django.contrib import messages
from django.http import JsonResponse
import uuid
from razorpay_integration.views import order_payment
from razorpay_integration.constants import PaymentStatus
from django.db.models import Max
from datetime import timedelta
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator
from datetime import datetime

@login_required
# @verification_required
@never_cache
def user_home(request,id):
    if request.user.is_authenticated:
        InstantBuy.objects.all().delete()
        Cart.objects.filter(customer_id=id).update(selected=False)
        user = CustomUser.objects.get(id=id)
        return render(request, 'userside/home.html', {'user':user})
    else:
        return redirect('userlogin')

def display_product(request, name, customer_id):
    if not request.user.is_authenticated:
        return redirect('userlogin')
    InstantBuy.objects.all().delete()
    user = CustomUser.objects.get(id=customer_id)
    category = Category.objects.get(category_name=name)
    Cart.objects.filter(customer=user).update(selected=False)
    if category.category_status is True:
        subcategory = SubCategory.objects.filter(category=name, sub_category_status=True)
        products = Product.objects.filter(product_category=category, product_status=True)
        paginator = Paginator(products, 4)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        favourites = Favourites.objects.filter(customer=customer_id)
        range = 'all'
        return render(request, 'userside/product.html',{'products':page_obj,'category':category,'subcategory':subcategory,'user':user,'range':range,'favourites':favourites})
    return redirect('/')

def display_sc_products(request, c_name, sc_name):
    if not request.user.is_authenticated:
        return redirect('userlogin')
    InstantBuy.objects.all().delete()
    category = Category.objects.get(category_name=c_name)
    sub_category = SubCategory.objects.get(category=category, sub_category_name=sc_name)
    Cart.objects.filter(customer_id=request.user.id).update(selected=False)
    if sub_category.sub_category_status is True:
        products = Product.objects.filter(product_sub_category=sub_category.id, product_status=True)
        paginator = Paginator(products, 4)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        subcategory = SubCategory.objects.filter(category=sub_category.category,sub_category_status=True)
        favourites = Favourites.objects.filter(customer=request.user.id)
        range = 'sc'
        return render(request, 'userside/product.html',{'products':page_obj,'category':sub_category.category,'subcategory':subcategory,'range':range,'favourites':favourites})
    
    return redirect('user-d-product', sub_category.category)

def display_product_details(request, productid, userid):
    if not request.user.is_authenticated:
        return redirect('userlogin')
    InstantBuy.objects.all().delete()
    user = CustomUser.objects.get(id=userid)
    details = Product.objects.get(id=productid)
    Cart.objects.filter(customer_id=userid).update(selected=False)
    return render(request, 'userside/productdetails.html',{'details':details,'user':user})

def display_cart(request, id):
    if not request.user.is_authenticated:
        return redirect('userlogin')
    total_price_sum = Cart.objects.filter(customer=id).aggregate(total=Sum('total_price')).get('total', 0)
    Cart.objects.filter(customer_id=id).update(selected=True)
    cart_items = Cart.objects.filter(customer_id=id).order_by('id')
    return render(request, 'userside/cart.html',{'cart_items':cart_items,'total':total_price_sum})

def add_to_cart(request, product_id, customer_id, quantity, range):
    customer = CustomUser.objects.get(id=customer_id)
    product = Product.objects.get(id=product_id)
    if Cart.objects.filter(customer=customer,product=product):
        print('entered')
        cart = Cart.objects.get(customer=customer,product=product)
        cart.quantity += quantity
        cart.unit_price = Product.objects.get(id=product_id).sales_price

        cart.total_price = (cart.unit_price*cart.quantity)
        cart.save()
        product = Product.objects.get(id=product_id)
        category = product.product_category
        print(range)
        if range == 'favourites':
            return redirect('userdisplaycart', customer_id)
        if range == 'all':
            return redirect('user-d-product', category, customer_id)
        if range == 'sc':
            return redirect('userdisplayscproducts', category, product.product_sub_category)
        if range == 'productdetails':
            return redirect('userdisplayproductdetails', product_id, customer_id)
        return redirect('user-d-product', category, customer_id)

    unit_price = Product.objects.get(id=product_id).sales_price
    total_price = (unit_price*quantity)
    cart = Cart(customer=customer, product=product, quantity=quantity, unit_price=unit_price, total_price=total_price)
    cart.save()
    category = product.product_category
    print(range)
    if range == 'favourites':
        return redirect('userdisplaycart', customer_id)
    return redirect('user-d-product', category, customer_id)

def update_cart_quantity(request, product_id, user_id, method):
    print(method)
    cart = Cart.objects.get(customer=user_id,product=product_id)
    if method == 'Add':
        if cart.quantity > 0:
            cart.quantity += 1
            cart.total_price = cart.quantity*cart.unit_price
            cart.save()
    if method == 'Remove':
        if cart.quantity > 1:
            cart.quantity -= 1
            cart.total_price = cart.quantity*cart.unit_price
            cart.save()
    return redirect('userdisplaycart', user_id)


def delete_from_cart(request, id, userid):
    item = Cart.objects.filter(product=id)
    item.delete()
    return redirect('userdisplaycart', userid)

def display_favourite_product(request, user_id):
    favourites = Favourites.objects.filter(customer=user_id)
    print(favourites)
    return render(request, 'userside/favourites.html', {'favourites': favourites, 'range':'favourites'})


def favourite_product(request, user_id, product_id, range):
    product = Product.objects.get(id=product_id)
    customer = CustomUser.objects.get(id=user_id)
    try:
        if Favourites.objects.get(customer=customer, product=product):
            Favourites.objects.get(customer=customer, product=product).delete()
    except:
        Favourites(customer=customer, product=product).save()
    
    if range == 'all':
        return redirect('user-d-product', product.product_category, user_id)
    elif range == 'sc':
        return redirect('userdisplayscproducts', product.product_category, product.product_sub_category)
    else:
        return redirect('displayfavouriteproduct', user_id)


def checkout(request, id, discount):
    range = 'checkout'
    if request.method == 'POST':
        selected_checkboxes = request.POST.getlist('check[]')
        Cart.objects.filter(customer_id=id).exclude(id__in=selected_checkboxes).update(selected=False)
    user_details = CustomUser.objects.get(id=id)
    try:
        address = Address.objects.get(customer=user_details, active_address=True)
    except:
        # return redirect('displayaddress', id)
        address = None
        cart_items = Cart.objects.filter(customer_id=id, selected=True)
        for item in cart_items:
            if item.quantity <= item.product.stock:
                pass
            else:
                messages.success(request, '{{product.product_name}} is out of stock')
                return redirect('userdisplaycart', id)
        total_price_sum = cart_items.aggregate(total=Sum('total_price')).get('total', 0) or 0
        count = Cart.objects.filter(customer=user_details).count()
        total_payable = total_price_sum + 20 - round(float(discount))
        return render(request, 'userside/checkout.html',{'user':user_details,'address':address,'totalprice':total_price_sum,'totalcount':count,'discount':float(discount),'totalpayable':total_payable,'cart_items':cart_items,'range':range})
    
    cart_items = Cart.objects.filter(customer_id=id, selected=True)
    address = Address.objects.get(customer=user_details, active_address=True)
    for item in cart_items:
        if item.quantity <= item.product.stock:
            pass
        else:
            messages.success(request, '{{product.product_name}} is out of stock')
            return redirect('userdisplaycart', id)
    total_price_sum = cart_items.aggregate(total=Sum('total_price')).get('total', 0) or 0
    count = Cart.objects.filter(customer=user_details).count()
    total_payable = total_price_sum + 20 - round(float(discount))
    return render(request, 'userside/checkout.html',{'user':user_details,'address':address,'totalprice':total_price_sum,'totalcount':count,'discount':float(discount),'totalpayable':total_payable,'cart_items':cart_items,'range':range})


def direct_checkout(request, product_id, range, user_id):
    if request.user.is_authenticated:
        customer = CustomUser.objects.get(id=user_id)
        if range == 'fromaddress':
            instantbuy = InstantBuy.objects.get(customer=user_id, selected=True)
            product = Product.objects.get(product_name=instantbuy.product.product_name)
            if product.stock > 0:
                pass
            else:
                messages.warning(request, '{{ product.product_name }} is out of stock')
                return redirect('userdisplayproductdetails', product, user_id)
            address = Address.objects.get(customer=customer, active_address=True)
            total_price_sum = product.sales_price
            total_payable = total_price_sum + 20 - round(float(0.0))
            range = 'directcheckout'
            instantbuy = InstantBuy.objects.filter(customer=user_id, selected=True)
            return render(request, 'userside/checkout.html',{'user':customer,'address':address,'totalprice':total_price_sum,'totalcount':1,'discount':float(0.0),'totalpayable':total_payable,'cart_items':instantbuy,'range':range})
        product_id = int(product_id)
        InstantBuy.objects.all().delete()
        product = Product.objects.get(id=product_id)
        if product.stock > 0:
            pass
        else:
            messages.warning(request, '{{ product.product_name }} is out of stock')
            return redirect('userdisplayproductdetails', product_id, user_id)
        instantbuy = InstantBuy(customer=customer, product=product, quantity=1, unit_price=product.product_price, total_price=product.sales_price, selected=True)
        instantbuy.save()
        try:
            if Address.objects.get(customer=customer, active_address=True):
                pass
        except:
            # return redirect('addaddress', user_id)
            address = None
            instantbuy = InstantBuy.objects.filter(customer=customer, selected=True)
            total_price_sum = product.sales_price
            total_payable = total_price_sum + 20 - round(float(0.0))
            range = 'directcheckout'
            return render(request, 'userside/checkout.html',{'user':customer,'address':address,'totalprice':total_price_sum,'totalcount':1,'discount':float(0.0),'totalpayable':total_payable,'cart_items':instantbuy,'range':range})
        address = Address.objects.get(customer=customer, active_address=True)
        
        instantbuy = InstantBuy.objects.filter(customer=customer, selected=True)
        total_price_sum = product.sales_price
        total_payable = total_price_sum + 20 - round(float(0.0))
        range = 'directcheckout'
        return render(request, 'userside/checkout.html',{'user':customer,'address':address,'totalprice':total_price_sum,'totalcount':1,'discount':float(0.0),'totalpayable':total_payable,'cart_items':instantbuy,'range':range})


def apply_coupon(request, id, amount, payableamount):
    if request.method == 'POST':
        code = request.POST['couponcode']
        print('success')
        try:
            if Coupon.objects.get(coupon_code=code).DoesNotExist():
                pass
        except:
            allowance_discount = 0
            cart_items = Cart.objects.filter(customer_id=id, selected=True)
            total_price_sum = cart_items.aggregate(total=Sum('total_price')).get('total', 0) or 0
            total_payable = total_price_sum + 20
            response_data = {
            'message': 'Success',
            'code': code,
            'allowance_discount': allowance_discount,
            'payable_amount': total_payable,
            'couponcode': code,
            }
            return JsonResponse(response_data)
        
        coupon = Coupon.objects.get(coupon_code=code)
        if coupon.min_purchase <= float(amount):
            if coupon.is_price_based:
                allowance_discount = coupon.discount_price
            else:
                allowance_discount = float(amount) * coupon.discount_percentage / 100
        else:
            return HttpResponse('Your not eligible to apply this coupon')

        payableamount = float(payableamount)-allowance_discount
        payableamount = round(payableamount, 2)
        # payableamount -= allowance_discount

        response_data = {
        'message': 'Success',
        'code': code,
        'allowance_discount': allowance_discount,
        'payable_amount': payableamount,
        'couponcode': code,
        }

        return JsonResponse(response_data)
    

def account_details(request, id):
    if request.user.is_authenticated:
        user = CustomUser.objects.get(id=id)
        return render(request, 'userside/accountdetails.html',{'user':user})
    else:
        return redirect('userlogin')

def update_user_details(request, id):
    if request.method == 'POST':
        name = request.POST['username']
        phone = request.POST['phone']
        email = request.POST['email']

        user = CustomUser.objects.get(id=id)
        user.name = name
        user.save()
        if CustomUser.objects.filter(email=email).exists():
            messages.success(request, 'email already exist')
            return redirect('accountdetails', id)
        user.email = email
        user.save()
        messages.success(request, 'Successfully updated')
        return redirect('accountdetails', id)
    return redirect('accountdetails', id)

def update_user_password(request, id):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        user = CustomUser.objects.get(id=id)
        if password != confirm_password:
            messages.success(request, 'properly enter the password')
            return redirect('updateuserpassword', id)
        elif len(password) < 8:
            print("Password must be at least 8 characters long.")
            return redirect('updateuserpassword', id)
        elif not any(char.isdigit() for char in password):
            print("Password must contain at least one digit.")
            return redirect('updateuserpassword', id)
        elif not any(char.isalpha() for char in password):
            print("Password must contain at least one letter.")
            return redirect('updateuserpassword', id)
        else:
            pass

        try:
            print('validating')
            validate_password(password)
        except ValidationError as e:
            # Handle validation error
            error_message = ', '.join(e.messages)
            print(f"Password validation failed: {error_message}")
            return redirect('updateuserpassword', id)
        print('entered')
        user.password = make_password(password)
        print(make_password(password))
        user.save()
        messages.success(request, 'Successfully updated')
        return redirect('accountdetails', id)
    return redirect('accountdetails', id)

@never_cache
def display_address(request, id):
    if request.user.is_authenticated:
        user_address = Address.objects.filter(customer=id).order_by('id')
        return render(request, 'userside/displayaddress.html',{'addresses':user_address})
    else:
        return redirect('userlogin')

def add_address(request, id, range):
    if request.method == 'POST':
        address_name = request.POST['addressname']
        name = request.POST['username']
        phone = request.POST['phone']
        pincode = request.POST['pincode']
        building = request.POST['building']
        area = request.POST['area']
        landmark = request.POST['landmark']
        city = request.POST['city']
        state = request.POST['state']


        if len(pincode) != 6 or type(pincode) != str:
            messages.success(request, 'pincode must be 6 digits')
            if range == 'checkout':
                return redirect('checkout', id, 0.0)
            else:
                return redirect('displayaddress', id)
                
        user = CustomUser.objects.get(id=id)
        Address.objects.filter(customer=id).update(active_address=False)
        new_address = Address(customer=user, address_name=address_name, full_name=name, mobile=phone, pincode=pincode, building=building, area=area, landmark=landmark, city=city, state=state)
        new_address.active_address = True
        new_address.save()
        print('completed')
    if range == 'checkout':
        return redirect('checkout', id, 0.0)
    if range == 'directcheckout':
        return redirect('directcheckout', None, 'fromaddress', id)
    else:
        return redirect('displayaddress', id)


def update_default_address(request, id):
    Address.objects.filter(customer=id).update(active_address=False)
    address = Address.objects.get(id=id)
    address.active_address = True
    address.save()
    return redirect('displayaddress', address.customer.id)


def update_address(request, id):
    print('enters')
    address = Address.objects.get(id=id)
    if request.method == 'POST':
        print('true')
        address_name = request.POST['addressname']
        name = request.POST['username']
        phone = request.POST['phone']
        pincode = request.POST['pincode']
        building = request.POST['building']
        area = request.POST['area']
        landmark = request.POST['landmark']
        city = request.POST['city']
        state = request.POST['state']

        address.address_name = address_name
        address.full_name = name
        address.mobile = phone
        address.pincode = pincode
        address.building = building
        address.area = area
        address.landmark = landmark
        address.city = city
        address.state = state
        address.save()
    
    return redirect('displayaddress', address.customer.id)

def delete_address(request, id, address_id):
    try:
        item = Address.objects.get(id=address_id)
        item.delete()
    except:
        messages.warning(request, 'This address has already in use')
    return redirect('displayaddress', id)

def place_order(request, id, final_amount, coupon_code, payment_mode):
    cart_items = Cart.objects.filter(customer=id, selected=True)
    customer = CustomUser.objects.get(id=id)
    if coupon_code is not None:
        try:
            if Coupon.objects.get(coupon_code=coupon_code):
                coupon = Coupon.objects.get(coupon_code=coupon_code)
        except:
            coupon = False
    else:
        pass
    
    address = Address.objects.get(customer=customer, active_address=True)
    if coupon == False:
        bulk_order = BulkOrder(bulk_order=uuid.uuid4(), address=address, payment_status=False, final_amount=final_amount)
        print(bulk_order)
    else:
        print(final_amount)
        if coupon.is_price_based:
            final_amount = float(final_amount) - coupon.discount_price
        else:
            final_amount = float(final_amount) - int(float(final_amount) * (coupon.discount_percentage/100))
        print(final_amount)
        bulk_order = BulkOrder(bulk_order=uuid.uuid4(), coupon=coupon, address=address, payment_status=False, final_amount=final_amount)
        
    bulk_order.final_amount = round(float(bulk_order.final_amount), 2)
    bulk_order.save()
    if InstantBuy.objects.filter(customer=customer, selected=True):
        instantbuy = InstantBuy.objects.filter(customer=customer, selected=True)
        max_duration = instantbuy.aggregate(max_duration=Max('product__duration'))['max_duration']
        for item in instantbuy:
            product = Product.objects.get(id=item.product.id)
            if item.quantity <= product.stock:
                pass
            else:
                messages.success(request, '{{product.product_name}} is out of stock')
                return redirect('userdisplayproductdetails', product.id, id)
    if cart_items:
        max_duration = cart_items.aggregate(max_duration=Max('product__duration'))['max_duration']
        for item in cart_items:
            product = Product.objects.get(id=item.product.id)
            if item.quantity <= product.stock:
                pass
            else:
                messages.success(request, '{{product.product_name}} is out of stock')
                return redirect('userdisplaycart', id)
            
    if payment_mode == 'wallet':
        wallet = Wallet.objects.get(customer=customer)
        if float(final_amount) > wallet.amount:
            messages.success(request, "your wallet doesn't have sufficient balance")
            return redirect('checkout', customer.id, 0.0)
        else:
            if InstantBuy.objects.filter(customer=customer, selected=True):
                instantbuy = InstantBuy.objects.filter(customer=customer, selected=True)
                for item in instantbuy:
                    product = Product.objects.get(id=item.product.id)
                    if item.quantity <= product.stock:
                        product.stock -= item.quantity
                        total_amount = product.sales_price*item.quantity
                        order = Order(customer=customer, product=product, quantity=item.quantity, order_status='requesting', payment_status=True, amount=item.unit_price, total_amount=total_amount, bulk_order=bulk_order)
                        order.save()
                        wallet.amount -= round(float(final_amount), 2)
                        wallet.save()
                        product.save()
                        InstantBuy.objects.all().delete()
                    else:
                        messages.success(request, '{{product.product_name}} is out of stock')
                average_tax_amount = Order.objects.filter(bulk_order=bulk_order).aggregate(Avg('tax_amount'))['tax_amount__avg']
                print(average_tax_amount)
            else:
                for item in cart_items:
                    product = Product.objects.get(id=item.product.id)
                    if item.quantity <= product.stock:
                        product.stock -= item.quantity
                        print(item.quantity)
                        total_amount = product.sales_price*item.quantity
                        order = Order(customer=customer, product=product, quantity=item.quantity, order_status='requesting', payment_status=True, amount=product.product_price, total_amount=total_amount, bulk_order=bulk_order)
                        order.save()
                        wallet.amount -= round(float(final_amount), 2)
                        wallet.save()
                        product.save()
                        Cart.objects.filter(customer=id, selected=True, product=item.product.id).delete()
                    else:
                        messages.success(request, '{{product.product_name}} is out of stock')
                average_tax_amount = Order.objects.filter(bulk_order=bulk_order).aggregate(Avg('tax_amount'))['tax_amount__avg']
                print(average_tax_amount)

            bulk = BulkOrder.objects.get(bulk_order=bulk_order.bulk_order)
            bulk.payment_status = True
            bulk.tax_amount = average_tax_amount
            bulk.save()
            transaction = Transaction(bulk_order=bulk_order, transaction_mode='wallet', transaction_amount=bulk.final_amount, transaction_date=datetime.now(), transaction_status=PaymentStatus.SUCCESS)
            transaction.save()
            order_status = PaymentStatus.SUCCESS
            
            
    if payment_mode == 'cash_on_delivery':
        print('cod')
        if InstantBuy.objects.filter(customer=customer, selected=True):
            instantbuy = InstantBuy.objects.filter(customer=customer, selected=True)
            for item in instantbuy:
                product = Product.objects.get(id=item.product.id)
                if item.quantity <= product.stock:
                    product.stock -= item.quantity
                    total_amount = product.sales_price*item.quantity
                    order = Order(customer=customer, product=product, quantity=item.quantity, order_status='requesting', payment_status=False, amount=item.unit_price, total_amount=total_amount, bulk_order=bulk_order)
                    order.save()
                    product.save()
                    InstantBuy.objects.all().delete()
                else:
                    messages.success(request, '{{product.product_name}} is out of stock')
            average_tax_amount = Order.objects.filter(bulk_order=bulk_order).aggregate(Avg('tax_amount'))['tax_amount__avg']
            print(average_tax_amount)
        else:
            for item in cart_items:
                product = Product.objects.get(id=item.product.id)
                if item.quantity <= product.stock:
                    product.stock -= item.quantity
                    print(item.quantity)
                    total_amount = product.sales_price*item.quantity
                    order = Order(customer=customer, product=product, quantity=item.quantity, order_status='requesting', payment_status=False, amount=product.product_price, total_amount=total_amount, bulk_order=bulk_order)
                    order.save()
                    product.save()
                    Cart.objects.filter(customer=id, selected=True, product=item.product.id).delete()
                else:
                    messages.success(request, '{{product.product_name}} is out of stock')
            average_tax_amount = Order.objects.filter(bulk_order=bulk_order).aggregate(Avg('tax_amount'))['tax_amount__avg']
            print(average_tax_amount)

        bulk = BulkOrder.objects.get(bulk_order=order.bulk_order.bulk_order)
        bulk.tax_amount = average_tax_amount
        bulk.save()
        order_status = PaymentStatus.PENDING

    address = customer.address_set.get(customer=customer.id, active_address=True)
    try:
        bulk_order_time = bulk_order.date + max_duration
        bulk_order.delivery_date = bulk_order_time
        bulk_order.save()
    except:
        return redirect('home', request.user.id)
    
    if payment_mode == 'razorpay':
        print('online')
        final_amount = str(final_amount)
        return order_payment(request, customer.id, final_amount, bulk_order)
    return render(request, "razorpay_integration/callback.html", context={"customer":customer, "status": order_status, "bulk_order": bulk_order})
    

def display_orders(request, id):
    orders = Order.objects.filter(customer=id)
    bulkorders = BulkOrder.objects.filter(bulk_order__in=orders.values_list('bulk_order', flat=True))
    first_orders = []
    for bulk in bulkorders:
        if not Order.objects.filter(bulk_order=bulk).exclude(order_status='cancelled').exists():
            first_order = Order.objects.filter(bulk_order=bulk).first()
        else:
            first_order = Order.objects.filter(bulk_order=bulk).exclude(order_status='cancelled').first()
        
        if not Order.objects.filter(bulk_order=bulk).exclude(order_status='cancelled').exists() or not Order.objects.filter(bulk_order=bulk).exclude(order_status='delivered').exists():
            status = 'completed'
        else:
            status = 'in progress'
        first_orders.append((first_order, status))
    return render(request, 'userside/userorders.html',{'first_orders':first_orders})


def order_details(request, order_id):
    order = Order.objects.get(id=order_id)
    orders = Order.objects.filter(bulk_order=order.bulk_order)
    valid_orders = Order.objects.filter(bulk_order=order.bulk_order).exclude(order_status__in=['cancelled','returned'])
    product_total = 0
    for ord in valid_orders:
        product_total += (ord.quantity * ord.product.sales_price)
    bulk_order = BulkOrder.objects.get(bulk_order=order.bulk_order.bulk_order)
    if bulk_order.delivery_charge:
        order_total = product_total + bulk_order.delivery_charge
    else:
        order_total = product_total + 0
    if bulk_order.coupon:
        if bulk_order.coupon.is_price_based:
            coupon_amount = bulk_order.coupon.discount_price
        else:
            total = Order.objects.filter(bulk_order=bulk_order).exclude(order_status__in=['cancelled','returned']).aggregate(total=Sum('total_amount')).get('total', 0) or 0
            total += bulk_order.delivery_charge
            coupon_amount = round(total * (bulk_order.coupon.discount_percentage/100), 2)
    else:
        coupon_amount = 0.0
    return render(request, 'userside/userorderdetails.html',{'order':order ,'orders':orders,'bulk_order':bulk_order,'product_total':product_total, 'order_total': order_total, 'coupon_amount':coupon_amount})


def user_order_status(request, order_id, status):
    print(status)
    order = Order.objects.get(id=order_id)
    wallet = Wallet.objects.get(customer=request.user.id)
    order_count = Order.objects.filter(bulk_order=order.bulk_order).count()
    bulk_order = BulkOrder.objects.get(bulk_order=order.bulk_order.bulk_order)
    delivery_charge = bulk_order.delivery_charge
    if status == 'cancel':
        print('c')
        order.order_status = 'cancelled'
        order.save()
        
    if status == 'return':
        print('r')
        order.order_status = 'returned'
        order.save()
    
    total_amount =  Order.objects.filter(bulk_order=bulk_order).exclude(Q(order_status='cancelled') | Q(order_status='returned')).aggregate(total_amount=Sum('total_amount'))['total_amount']
    print(total_amount)
    if total_amount:
        print(total_amount)
        bulk_order.final_amount = round(total_amount, 2) + bulk_order.delivery_charge
    bulk_order.tax_amount = bulk_order.final_amount / (1 + (bulk_order.tax_rate / 100))
    order_exist_check = Order.objects.filter(bulk_order=bulk_order).exclude(Q(order_status='cancelled') | Q(order_status='returned'))
    if order_exist_check:
        pass
    else:
        bulk_order.delivery_charge = None
        bulk_order.final_amount = None
    try:
        if bulk_order.final_amount >= bulk_order.coupon.min_purchase:
            pass
        else:
            bulk_order.coupon = None
    except:
        pass
        
    if order.payment_status is True:
        wallet.amount += order.total_amount - delivery_charge
        transaction = Transaction.objects.filter(bulk_order=order.bulk_order)
        transaction.transaction_amount -= (order.total_amount - delivery_charge)
        transaction.save()
        
    product = Product.objects.get(id=order.product.id)
    product.stock += 1

    bulk_order.save()
    product.save()
    order.save()
    wallet.save()
    return redirect('userorderdetails', order_id)


def search_product(request):
    if request.method == 'POST':
        print('hello')
        search = request.POST['search']
        product = Product.objects.filter(product_status=True, product_name__istartswith=search)
        user = CustomUser.objects.get(id=request.user.id)
        categories = Category.objects.filter(category_status=True)
        is_category_status_true = Category.objects.filter(category_status=True).exists()
        Cart.objects.filter(customer=user).update(selected=False)
        if is_category_status_true:
            # paginator = Paginator(product, 4)

            # page_number = request.GET.get('page')
            # page_obj = paginator.get_page(page_number)
            favourites = Favourites.objects.filter(customer=user.id)
            range = 'all'
            return render(request, 'userside/product.html',{'products':product,'category':categories,'subcategory':None,'user':user,'range':range,'favourites':favourites})
        return redirect('/')
    

def display_wallet(request, id):
    user = CustomUser.objects.get(id=id)
    try:
        if Wallet.objects.get(customer=user):
            pass
    except:
        Wallet(customer=user, amount=0.0).save()

    wallet = Wallet.objects.get(customer=id)
    return render(request, 'userside/displaywallet.html',{'wallet':wallet})

def single_order_details(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, 'userside/singleorderdetails.html',{'order':order})


