from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.urls import reverse
from adminside import urls as admin_urls

User = get_user_model()

class CommonMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # if not request.user.is_authenticated and request.user.is_anonymous and request.path not in [reverse('usersignin'), reverse('userlogin'), reverse('userotplogin'), reverse('adminsignin'), reverse('adminlogin'), reverse('adminotplogin'), reverse('dashboard')]:
        #     return redirect('userlogin')
        
        response = self.get_response(request)

        return response