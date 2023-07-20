from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from adminside.models import Product, ProductImage, Category, SubCategory
from userside.models import Cart, Coupon, BulkOrder, Order, Address, Transaction
from authentication.models import CustomUser
from django.contrib import messages
from datetime import timedelta, datetime, time
from dateutil.relativedelta import relativedelta
# import datetime
from razorpay_integration.constants import PaymentStatus
from django.db.models import Q
from django.db.models import Count
from django.db.models import Sum, F, FloatField, Subquery, OuterRef, DecimalField
import calendar
# Create your views here.

def base(request):
    if request.user.is_authenticated:
        orders = Order.objects.all().exclude(order_status__in=['cancelled','returned']).count()
        product = Product.objects.annotate(num_orders=Count('order',filter=~Q(order__order_status__in=['cancelled','returned'])))
        recent_orders = Order.objects.all().exclude(order_status__in=['cancelled','returned','delivered']).order_by('id')
        daily_start_date = datetime.combine(datetime.now().date(), time(hour=12))
        daily_end_date = daily_start_date + timedelta(days=1)
        daily_sales = Transaction.objects.filter(transaction_date__date__range=[daily_start_date, daily_end_date])
        total_daily_sales = daily_sales.aggregate(total_amount=Sum('transaction_amount'))['total_amount']
        daily_sales_count = daily_sales.count()
        if total_daily_sales:
            total_daily_sales = round(total_daily_sales, 3)
        else:
            total_daily_sales = 0.0
        
        categories = Category.objects.all()
        product_profit = Product.objects.annotate(
            total_profit=Subquery(
                Transaction.objects.filter(
                    bulk_order__order__product_id=OuterRef('pk')
                ).values('bulk_order__order__product_id').annotate(
                    total_amount=Sum('transaction_amount', output_field=DecimalField()),
                    cost_price=Sum(
                        F('bulk_order__order__product__sales_price') * F('transaction_amount') / F('bulk_order__order__product__product_price'),
                        output_field=DecimalField()
                    )
                ).values('bulk_order__order__product_id')
            )
        )
        weekly_start_date = daily_end_date - timedelta(days=7)
        weekly_sales = Transaction.objects.filter(transaction_date__date__range=[weekly_start_date, daily_end_date])
        weekly_sales_count = weekly_sales.count()

        weekday_names = []
        current_date = weekly_start_date
        while current_date <= daily_end_date:
            weekday_name = calendar.day_name[current_date.weekday()]
            weekday_names.append(weekday_name)
            current_date += timedelta(days=1)
        
        
        start_date = datetime(year=2023, month=1, day=1)
        end_date = start_date + relativedelta(years=1)
        monthly_sales = []
        current_date = start_date
        while current_date < end_date:
            month_start_date = current_date.replace(day=1)
            month_end_date = month_start_date + relativedelta(months=1) - timedelta(days=1)
            monthly_sale = Transaction.objects.filter(transaction_date__date__range=[month_start_date, month_end_date]).aggregate(total=Sum('transaction_amount'))
            month_name = current_date.strftime('%B')  # Get the name of the month
            monthly_sales.append({'month': month_name, 'total_sales': monthly_sale['total'] or 0})
            current_date += relativedelta(months=1)
        
        total_monthly_sales = sum(item['total_sales'] for item in monthly_sales)
        
        total_transaction = Transaction.objects.filter(transaction_status='Success').aggregate(total_amount=Sum('transaction_amount'))
        total_amount = total_transaction['total_amount']
        total_order_count = Transaction.objects.count()
        print(total_daily_sales, daily_sales_count, orders, weekday_names, weekly_sales, weekly_sales_count, monthly_sale, total_monthly_sales, total_amount)
        context = {
            'daily_sales': total_daily_sales,
            'daily_sales_count': daily_sales_count,
            'orders': orders,
            'categories': categories,
            'products': product,
            'recent_orders': recent_orders,
            'product_profit': product_profit,
            'weekday_names': weekday_names,
            'weekly_sales': weekly_sales,
            'weekly_sales_count': weekly_sales_count,
            'monthly_sales': monthly_sales,
            'total_monthly_sales': total_monthly_sales,
            'total_amount': total_amount,
            'total_count': total_order_count,
        }
        return render(request, 'adminside/adminhome.html', context)
    else:
        return render(request, 'authentication/adminlogin.html')
    
def index(request):
    return render(request, 'adminside/index.html')

def display_products(request):
    products = Product.objects.all().order_by('id')
    return render(request, 'adminside/displayproducts.html', {'products':products})

def add_product(request):
    if request.method == "POST":
        product_name = request.POST['product_title']
        product_category = request.POST['product_category']
        product_sub_category = request.POST['product_sub_category']
        product_label = request.POST['product_label']
        product_description = request.POST['product_description']
        product_status = request.POST['product_status']
        product_image1 = request.FILES.get('img-1')
        product_image2 = request.FILES.get('img-2')
        product_image3 = request.FILES.get('img-3')
        product_price = request.POST['product_price']
        sales_price = request.POST['sales_price']
        profit_margin = request.POST['profit_margin']
        stock = request.POST['stock']
        unit = request.POST['lastAction']
        
        if unit == 'pc':
            unit = True
            weight = None
            piece = request.POST['piece']
        else:
            unit = False
            piece = None
            weight = request.POST['weight']

        duration_minutes = int(request.POST['duration'])
        hours = duration_minutes // 60
        minutes = duration_minutes % 60

        duration_str = f"{hours}:{minutes:02}"
        print(duration_minutes)
        print(duration_str)
        total_energy = request.POST['total_energy']
        carbohydrate = request.POST['carbohydrate']
        fat = request.POST['fat']
        protein = request.POST['protein']

        try:
            if Product.objects.get(product_name=product_name):
                messages.success(request, 'Product name already exist')
                return redirect('add-product')
        except:
            pass

        if Category.objects.filter(category_name=product_category).exists():
            category = Category.objects.get(category_name=product_category)
        else:
            return redirect('add-category')
        
        if SubCategory.objects.filter(sub_category_name=product_sub_category).exists():
            sub_category = SubCategory.objects.get(sub_category_name=product_sub_category, category=category)
        else:
            return redirect('add-sub-category')
        
        try:
            if SubCategory.objects.get(sub_category_name=product_sub_category, category=category):
                pass
        except:
            messages.success(request, 'Error')
            return redirect('add-product')

        images = ProductImage(image1 = product_image1, image2 = product_image2, image3 = product_image3)
        images.save()
        

        product = Product(product_name=product_name,product_category=category, product_sub_category=sub_category, product_label=product_label, product_description=product_description,
                          product_status=product_status,product_image_id=images,
                          product_price=product_price,sales_price=sales_price,profit_margin=profit_margin,stock=stock,unit=unit,piece=piece,weight=weight,
                          duration=duration_str,total_energy=total_energy,carbohydrate=carbohydrate,fat=fat,protein=protein)
        product.save()
        
        return redirect('d-products')
    
    print("no")
    categories = Category.objects.all()
    sub_categories = SubCategory.objects.all()
    return render(request, 'adminside/addproducts.html',{'categories':categories,'subcategories':sub_categories})



def update(request, id):
    product = Product.objects.get(id=id)
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()
    default_unit = 'pc' if product.unit else 'wgt'
    duration = product.duration
    converted_minutes = duration.total_seconds() // 60
    template = loader.get_template('adminside/updateproduct.html')
    context = {
        'product': product,
        'categories': categories,
        'subcategories': subcategories,
        'converted_minutes': round(converted_minutes),
        'default_unit': default_unit
    }
    return HttpResponse(template.render(context, request))
    

def update_product(request, id):
    if request.method == 'POST':
        product_name = request.POST['product_title']
        product_category = request.POST['product_category']
        product_sub_category = request.POST['product_sub_category']
        product_label = request.POST['product_label']
        product_description = request.POST['product_description']
        product_status = request.POST['product_status']
        product_price = request.POST['product_price']
        sales_price = request.POST['sales_price']
        profit_margin = request.POST['profit_margin']
        stock = request.POST['stock']
        unit = request.POST['lastAction']
        
        if unit == 'pc':
            unit = True
            weight = None
            piece = request.POST['piece']
        else:
            unit = False
            piece = None
            weight = request.POST['weight']
        duration_minutes = int(request.POST['duration'])
        hours = duration_minutes // 60
        minutes = duration_minutes % 60

        duration_str = f"{hours}:{minutes:02}"
        print(duration_minutes)
        print(duration_str)
        total_energy = request.POST['total_energy']
        carbohydrate = request.POST['carbohydrate']
        fat = request.POST['fat']
        protein = request.POST['protein']

        try:
            if not Category.objects.get(category_name=product_category):
                messages.success(request, "subcategory in this category don't exist")
                raise ValueError()
            if not SubCategory.objects.get(category = product_category, sub_category_name = product_sub_category):
                messages.success(request, "category with this subcategory don't exist")
                raise ValueError()
        except:
            messages.success(request, "error in matching category and subcategory")
            return redirect('u-product', id)
        if float(stock) < 0:
            messages.warning(request, "You have entered negative value, please try again")
            return redirect('u-product', id)
        
        product = Product.objects.get(id=id)
        product.product_name = product_name
        product.product_category = Category.objects.get(category_name=product_category)
        product.product_sub_category = SubCategory.objects.get(category = product_category, sub_category_name = product_sub_category)
        product.product_label = product_label
        product.product_description = product_description
        product.product_status = product_status
        product.product_price = product_price
        product.sales_price = sales_price
        product.profit_margin = profit_margin
        product.stock = stock
        product.unit = unit
        product.piece = piece
        product.weight = weight
        product.duration = duration_str
        product.total_energy = total_energy
        product.carbohydrate = carbohydrate
        product.fat = fat
        product.protein = protein
        product.save()


        if 'img-1' in request.FILES or 'img-2' in request.FILES or 'img-3' in request.FILES:
            images = ProductImage.objects.get(id=product.product_image_id.id)

            if 'img-1' in request.FILES:
                images.image1 = request.FILES['img-1']
            if 'img-2' in request.FILES:
                images.image2 = request.FILES['img-2']
            if 'img-3' in request.FILES:
                images.image3 = request.FILES['img-3']

            images.save()
        
        try:
            if Cart.objects.get(product=product.id):
                cart = Cart.objects.get(product=product.id)
                cart.unit_price = product.sales_price
                cart.unit_price = float(cart.unit_price)
                cart.total_price = (float(cart.quantity)*cart.unit_price)
                cart.save()
        except:
            pass
        return redirect('d-products')
    return redirect('u-product', id)

def update_product_stock(request):
    if request.method == 'POST':
        stock = request.POST['stock']
        product_id = request.POST['product']
        product = Product.objects.get(id=product_id)
        product.stock = stock
        product.save()
    return redirect('d-products')

def product_subcategory_update(request, category):
    if request.method == 'GET':
        subcategories = SubCategory.objects.filter(category=category).values_list('sub_category_name', flat=True)
        response_data = {
            'subcategories': list(subcategories),
        }
        return JsonResponse(response_data)

def update_status(request, id):
    product = Product.objects.get(id=id)
    if product.product_status == False:
        product.product_status = True
    else:
        product.product_status = False

    product.save()
    return redirect('d-products')


def product_details(request,id):
    product = Product.objects.get(id=id)
    print(product)
    return render(request,'adminside/productdetails.html',{'product':product})


def display_category(request):
    categories = Category.objects.all()
    return render(request, 'adminside/displaycategory.html',{'categories': categories})


def add_category(request):
    if request.method == 'POST':
        category_name = request.POST['category_name']
        category_status = request.POST['category_status']

        category_name = category_name.upper()
        try:
            if Category.objects.get(category_name=category_name):
                messages.success(request, 'Category name already exist')
                return redirect('add-category')
        except:
            pass

        category = Category(category_name=category_name, category_status=category_status)
        category.save()
        return redirect('d-category')
    
    return render(request, 'adminside/addcategory.html')


def update_category(request, name):
    category = Category.objects.get(category_name=name)
    template = loader.get_template('adminside/updatecategory.html')
    context = {
        'category': category,
    }
    return HttpResponse(template.render(context, request))
    

def update_category_record(request, name):
    if request.method == 'POST':
        category_name = request.POST['category_name']
        category_status = request.POST['category_status']
        
        try:
            if Category.objects.get(category_name=category_name):
                return redirect('d-category', name)
        except:
            pass

        category = Category.objects.get(category_name=name)
        category.category_name = category_name
        category.category_status = category_status

        category.save()
        messages.success(request, 'Category '+ category_name +  ' updated successfully')
        return redirect('d-category')
    
    return redirect('u-category', name)


def update_category_status(request, name):
    category = Category.objects.get(category_name=name)
    if category.category_status == True:
        category.category_status = False
        messages.success(request, "Category "+ name + " blocked")
    else:
        category.category_status = True
        messages.success(request, "Category "+ name + " unblocked")
    
    category.save()
    return redirect('d-category')


def category_details(request, name):
    category = Category.objects.get(category_name=name)
    return render(request, 'adminside/categorydetails.html', {'category':category})


def display_sub_category(request, c_name):
    sub_categories = SubCategory.objects.filter(category=c_name)
    return render(request, 'adminside/displaysubcategory.html',{'sub_categories': sub_categories})


def add_sub_category(request):
    if request.method == 'POST':
        sub_category_name = request.POST['sub_category_name']
        category_name = request.POST['category']
        sub_category_status = request.POST['sub_category_status']
        sub_category_img = request.FILES.get('sub_c_img')

        try:
            if SubCategory.objects.get(sub_category_name=sub_category_name, category=category_name):
                messages.success(request, 'SubCategory name already exist with this category')
                return redirect('add-sub-category')
        except:
            pass

        category = Category.objects.get(category_name=category_name)
        category.save()
        sub_category = SubCategory(category=category, sub_category_name=sub_category_name, sub_category_status=sub_category_status, sub_category_image=sub_category_img)
        sub_category.save()
        return redirect('d-sub-category',category_name)
    
    return render(request, 'adminside/addsubcategory.html')


def update_sub_category(request, category_name, subcategory_name):
    category = Category.objects.get(category_name=category_name)
    sub_category = SubCategory.objects.get(category=category, sub_category_name=subcategory_name)
    template = loader.get_template('adminside/updatesubcategory.html')
    context = {
        'sub_category': sub_category,
    }
    return HttpResponse(template.render(context, request))


def update_sub_category_record(request, category_name, subcategory_name):
    if request.method == 'POST':
        sub_category_name = request.POST['sub_category_name']
        category = request.POST['category']
        sub_category_status = request.POST['sub_category_status']
        sub_category_img = request.FILES.get('sub_c_img')
        
        category = Category.objects.get(category_name=category_name)
        try:
            if SubCategory.objects.get(category=category, sub_category_name=sub_category_name):
                messages.success(request, 'SubCategory name already exist')
                return redirect('u-sub-category', category_name, subcategory_name)
        except:
            pass

        sub_category = SubCategory.objects.get(category=category, sub_category_name=subcategory_name)
        sub_category.sub_category_name = sub_category_name
        try:
            if SubCategory.objects.get(category=category, sub_category_name=sub_category_name):
                messages.success(request, 'SubCategory name already exist')
                return redirect('u-sub-category', category_name, subcategory_name)
        except:
            pass

        sub_category.category = category
        sub_category.sub_category_status = sub_category_status
        sub_category.sub_category_image = sub_category_img

        sub_category.save()
        return redirect('d-sub-category', category_name)
    
    return redirect('u-sub-category', category_name, subcategory_name)


def update_sub_category_status(request, category_name, subcategory_name):
    category=Category.objects.get(category_name=category_name)
    sub_category = SubCategory.objects.get(category=category, sub_category_name=subcategory_name)
    if sub_category.sub_category_status == True:
        sub_category.sub_category_status = False
    else:
        sub_category.sub_category_status = True
    
    sub_category.save()
    return redirect('d-sub-category', category_name)


def display_user(request):
    customers = CustomUser.objects.filter(is_admin=False)
    return render(request, 'adminside/displayuser.html',{'customers':customers})


def user_details(request,name):
    customer = CustomUser.objects.get(name=name, is_admin=False)
    try:
        address = Address.objects.get(customer=customer, active_address=True)
        return render(request, 'adminside/userdetails.html',{'customer':customer, 'address':address})
    except:
        address = None
        return render(request, 'adminside/userdetails.html',{'customer':customer, 'address':address})
    

def update_user_status(request,name):
    status = CustomUser.objects.get(name=name)
    if status.is_active == True:
        status.is_active = False
    else:
        status.is_active = True

    status.save()
    return redirect('user-details',status.name)


def display_coupon(request):
    coupons = Coupon.objects.all()
    return render(request, 'adminside/displaycoupon.html',{'coupons': coupons})


def add_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST['couponcode']
        expiry_date = request.POST['expirydate']
        min_purchase = request.POST['minpurchase']
        discount_type = request.POST['discounttype']
        discount_percentage = request.POST['discountpercentage']
        discount_price = request.POST['discountprice']
        
        try:
            if Coupon.objects.get(coupon_code=coupon_code):
                messages.success(request, 'Coupon name already exist')
                return redirect('displaycoupon')
        except:
            pass

        if discount_type == 'percentage':
            is_price_based = False
        if discount_type == 'price':
            is_price_based = True
        coupon = Coupon(coupon_code=coupon_code, expiry_date=expiry_date,is_price_based=is_price_based,discount_percentage=discount_percentage,discount_price=discount_price,min_purchase=min_purchase)
        coupon.save()
        return redirect('displaycoupon')
    
    return render(request, 'adminside/addcategory.html')


def display_offers(request):
    products = Product.objects.all()
    return render(request, 'adminside/displayoffers.html',{'products':products})

def add_offer(request, id):
    if request.method == 'POST':
        offer_type = request.POST['offertype']
        is_price_based = request.POST['offermethod']
        expire = request.POST['expire']

        if offer_type == 'product':
            product = request.POST['product']
            category = None
        if offer_type == 'category':
            category = request.POST['category']
            product = None
        
        if is_price_based:
            offer_price = request.POST['offerprice']
            offer_price = float(offer_price)
        else:
            offer_percentage = request.POST['offerpercentage']
            offer_percentage = float(offer_percentage)
        
        if offer_type == 'product':
            product = Product.objects.get(product_name=product)
            if is_price_based:
                product.offer_price = product.sales_price - offer_price
                product.expiry_date = expire
            else:
                product.offer_price = product.sales_price - (product.sales_price* (offer_percentage/100))
                product.expiry_date = expire
            product.save()
        if offer_type == 'category':
            products = Product.objects.filter(product_category=category)
            for product in products:
                if is_price_based:
                    product.offer_price = product.sales_price - offer_price
                    product.expiry_date = expire
                else:
                    product.offer_price = product.sales_price - (product.sales_price* (offer_percentage/100))
                    product.expiry_date = expire
                product.save()

        return redirect('displayoffers')
    
    return render(request, 'adminside/addcategory.html')

def display_orders(request):
    orders = Order.objects.all().order_by('-id')
    neworder = Order.objects.filter(order_status='requesting')
    return render(request, 'adminside/displayorders.html',{'orders':orders, 'neworder':neworder})

def display_order_details(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, 'adminside/displayorderdetails.html',{'order':order})


def update_order_status(request, order_id, status):
    print(status)
    print(order_id)
    order = Order.objects.get(id=order_id)
    if status == 'cancel':
        product = Product.objects.get(id=order.product.id)
        product.stock += 1
        product.save()
        order.order_status = 'cancelled'
    if status == 'requesting':
        print('1')
        order.order_status = 'confirmed'
    if status == 'confirmed':
        print('2')
        order.order_status = 'packed'
    if status == 'packed':
        print('3')
        order.order_status = 'shipped'
    if status == 'shipped':
        order.payment_status = True
        print('4')
        order.order_status = 'delivered'
        order.save()
        bulk_order = BulkOrder.objects.get(bulk_order=order.bulk_order.bulk_order)
        if bulk_order.payment_status == False:
            orders = Order.objects.filter(bulk_order=bulk_order.bulk_order).exclude(Q(order_status__in=['cancelled', 'returned']) | Q(payment_status=True))
            print(orders)
            if not orders:
                bulk_order.payment_status = True
                bulk_order.save()
                transaction = Transaction(bulk_order=bulk_order,transaction_mode='cod',transaction_amount=bulk_order.final_amount,transaction_date=datetime.now(),transaction_status=PaymentStatus.SUCCESS)
                transaction.save()
    order.save()
    return redirect('displayorders')