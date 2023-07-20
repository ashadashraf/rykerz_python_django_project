from django.urls import path, include
from razorpay_integration import views

urlpatterns = [
    # path('', views.razorpay_home, name='razorpayhome'),
    path('payment/<str:id>/<str:amount>/<int:bulk_order', views.order_payment, name='payment'),
    path('callback/<str:customer>/<str:amount>/<str:bulkorder>', views.callback, name='callback'),
]
