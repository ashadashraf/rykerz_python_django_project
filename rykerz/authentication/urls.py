from django.urls import path, include
from authentication import views

urlpatterns = [
    path('', views.user_login, name='userlogin'),
    path('userotplogin', views.user_otp_login, name='userotplogin'),
    path('userlogout', views.user_logout, name='userlogout'),
    path('usersignin', views.user_signin, name='usersignin'),
    path('adminsignin', views.admin_signin, name='adminsignin'),
    path('adminotplogin', views.admin_otp_login, name='adminotplogin'),
    path('adminlogin', views.admin_login, name='adminlogin'),
    path('adminlogout', views.admin_logout, name='adminlogout'),
    path('verify/<str:mobile>', views.verify_code, name='verify'),
]
