from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from userside.models import Order
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from django.contrib.auth.decorators import login_required

from .models import CustomUser, CustomUserManager
from userside.models import Wallet

# Create your views here.

client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])
verify = client.verify.services(os.environ['TWILIO_VERIFY_SERVICE_SID'])


def send(phone):
    verify.verifications.create(to=phone, channel='sms')



def check(phone, code):
    try:
        result = verify.verification_checks.create(to=phone, code=code)
    except TwilioRestException:
        print('no')
        return False
    return result.status == 'approved'


def user_signin(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        mobile = '+91' + request.POST['phone']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        print(password)
        
        if password != confirm_password:
            messages.success(request, 'properly enter the password')
            return redirect('usersignin')
        elif CustomUser.objects.filter(email=email).exists():
            messages.success(request, 'email already exist')
            return redirect('usersignin')
        elif CustomUser.objects.filter(mobile=mobile).exists():
            messages.success(request, 'mobile number already taken')
            return redirect('usersignin')
        elif CustomUser.objects.filter(name=name).exists():
            messages.success(request, 'username already taken')
            return redirect('usersignin')
        elif len(password) < 8:
            print("Password must be at least 8 characters long.")
            return redirect('usersignin')
        elif not any(char.isdigit() for char in password):
            print("Password must contain at least one digit.")
            return redirect('usersignin')
        elif not any(char.isalpha() for char in password):
            print("Password must contain at least one letter.")
            return redirect('usersignin')
        else:
            pass

        try:
            print('validating')
            validate_password(password)
        except ValidationError as e:
            # Handle validation error
            error_message = ', '.join(e.messages)
            print(f"Password validation failed: {error_message}")
            return redirect('usersignin')
        print('entered')
        try:
            print(mobile)
            send(mobile)
        except:
            return HttpResponse('Check your internet connetion or you have exceeded the twilio limit')
        user = CustomUser.objects._create_user(name=name, mobile=mobile, email=email, password=password)
        user.is_active=True
        user.is_user=True
        user.save()
        return redirect('verify',mobile=mobile)
        # return redirect('userlogin')
    
    if request.user.is_authenticated:
        return render(request, 'userside/home.html')
    else:
        return render(request, 'authentication/usersignin.html')

def user_login(request):
    if request.user.is_authenticated:
        return render(request, 'userside/home.html')
    if request.method == 'POST':
        print('yes')
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(email=email, password=password)
        print('yes')
        if user and user.is_user is True:
            user.is_active == True
            login(request,user)
            print('in')
            messages.success(request, 'login success')
            return redirect('home', user.id)
        else:
            print('out')
            if CustomUser.objects.filter(email=email):
                messages.warning(request, 'invalid password please try again')
            else:
                messages.warning(request, 'invalid email please try again')
            otp_login = False
            return render(request, 'authentication/userlogin.html',{'otp_login':otp_login})
    else:
        otp_login = False
        return render(request, 'authentication/userlogin.html',{'otp_login':otp_login})
    
def user_otp_login(request):
    if request.user.is_authenticated:
        return render(request, 'userside/home.html')
    if request.method == 'POST':
        mobile = '+91' + request.POST['phone']
        try:
            check = CustomUser.objects.get(mobile=mobile, is_active=True)
        except:
            messages.warning(request, 'mobile number does not exist')
            return redirect('userotplogin')
        
        if check.is_admin is True:
            otp_login = True
            messages.success(request,"You can't login with this number")
            return render(request, 'authentication/userlogin.html',{'otp_login':otp_login})
        if check:
            try:
                send(mobile)
            except:
                return HttpResponse('Check your internet connection')
        else:
            otp_login = True
            return render(request, 'authentication/userlogin.html',{'otp_login':otp_login})
        return redirect('verify',mobile=mobile)
    
    else:
        otp_login = True
        return render(request, 'authentication/userlogin.html',{'otp_login':otp_login})


def user_logout(request):
    logout(request)
    otp_login = False
    return render(request, 'authentication/userlogin.html',{'otp_login':otp_login})


def admin_signin(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        mobile = '+91' + request.POST['phone']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        print(password)
        
        if password != confirm_password:
            messages.success(request, 'password fields does not matching')
            return redirect('adminsignin')
        elif CustomUser.objects.filter(email=email).exists():
            messages.success(request, 'email already exist')
            return redirect('adminsignin')
        elif CustomUser.objects.filter(mobile=mobile).exists():
            messages.success(request, 'mobile number already taken')
            return redirect('adminsignin')
        elif CustomUser.objects.filter(name=name).exists():
            messages.success(request, 'username already taken')
            return redirect('adminsignin')
        elif len(password) < 8:
            messages.success(request, 'Password must be at least 8 characters long')
            return redirect('adminsignin')
        elif not any(char.isdigit() for char in password):
            messages.success(request, 'Password must contain at least one digit')
            return redirect('adminsignin')
        elif not any(char.isalpha() for char in password):
            messages.success(request, 'Password must contain at least one letter')
            return redirect('adminsignin')
        else:
            pass

        try:
            validate_password(password)
        except ValidationError as e:
            # Handle validation error
            error_message = ', '.join(e.messages)
            print(f"Password validation failed: {error_message}")
            return redirect('adminsignin')
        
        try:
            send(mobile)
        except:
            return HttpResponse('Check your internet connetion or you have exceeded the twilio limit')
        admin = CustomUser.objects._create_user(name=name, mobile=mobile, email=email, password=password)
        admin.is_superuser=True
        admin.is_user=False
        admin.is_admin=True
        admin.save()
        return redirect('verify',mobile=mobile)
        # return redirect('userlogin')
    
    if request.user.is_authenticated:
        return render(request, 'authentication/adminlogin.html')
    else:
        return render(request, 'authentication/adminsignin.html')


def admin_login(request):
    if request.user.is_authenticated and request.user.is_admin == True:
        return render(request, 'adminside/adminhome.html')
    
    if request.method == 'POST':
        email = request.POST['adminemail']
        password = request.POST['password']
        user = authenticate(email=email, password=password)
        if user and user.is_admin == True:
            orders = Order.objects.filter(customer_id=user.id)
            login(request, user)
            messages.success(request, 'Admin login success')
            return render(request, 'adminside/adminhome.html',{'orders': orders})
        else:
            if CustomUser.objects.filter(email=email, is_admin=True):
                messages.warning(request, 'Incorrect password')
            else:
                messages.warning(request, 'email does not exist')
            otp_login = False
            return render(request, 'authentication/adminlogin.html',{'otp_login':otp_login})
        
    otp_login = False
    return render(request, 'authentication/adminlogin.html', {'otp_login':otp_login})


def admin_otp_login(request):
    if request.user.is_authenticated:
        return render(request, 'adminside/adminhome.html')
    if request.method == 'POST':
        mobile = '+91' + request.POST['phone']
        check = CustomUser.objects.filter(mobile=mobile, is_admin=True)
        print(check)
        if check:
            try:
                send(mobile)
            except:
                messages.warning(request, 'cannot sent otp')
                return redirect('adminotplogin')
            return redirect('verify',mobile=mobile)
        else:
            messages.warning(request, 'mobile number does not exist')
            otp_login = True
            return render(request, 'authentication/adminlogin.html',{'otp_login':otp_login})
            
    
    else:
        otp_login = True
        return render(request, 'authentication/adminlogin.html',{'otp_login':otp_login})


def admin_logout(request):
    request.user.is_active = False
    logout(request)
    messages.success(request, 'Admin logout success')
    return render(request, 'authentication/adminlogin.html')


def verify_code(request, mobile):
    if request.method == 'POST':
        code = request.POST['otp']
        user = CustomUser.objects.get(mobile=mobile)
        if check(mobile, code):
            user = CustomUser.objects.get(mobile=mobile)
            user.is_verified = True
            user.is_active = True
            user.save()
            try:
                if Wallet.objects.get(customer=user):
                    pass
            except:
                Wallet(customer=user, amount=0.0).save()
            login(request, user)
        else:
            messages.warning(request, 'otp failed to login')
            to_be_deleted =  CustomUser.objects.filter(is_verified=False)
            del to_be_deleted
            return redirect('userotplogin')

        if user.is_verified is True and user.is_active is True and user.is_admin is False and user.is_user is True:
            messages.success(request, 'User verification success')
            return redirect('home', user.id)
        elif user.is_verified is True and user.is_active is True and user.is_admin is True and user.is_user is False:
            messages.success(request, 'Admin verification success')
            return redirect('dashboard')
        else:
            messages.success(request, 'You are not verified')
            return redirect('usersignin')
        
    if request.user.is_authenticated:
        person = CustomUser.objects.get(mobile=mobile)
        if person.is_admin is True and person.is_verified is True:
            return redirect('dashboard')
        else:
            return redirect('home')

    
    return render(request, 'authentication/verify.html', {'mobile':mobile})