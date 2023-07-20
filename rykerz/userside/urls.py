from django.urls import path
from userside import views

urlpatterns = [
    path('<int:id>', views.user_home, name='home'),
    path('user-d-product/<str:name>/<int:customer_id>', views.display_product, name='user-d-product'),
    path('userdisplayscproducts/<str:c_name>/<str:sc_name>', views.display_sc_products, name='userdisplayscproducts'),
    path('userdisplayproductdetails/<int:productid>/<int:userid>', views.display_product_details, name='userdisplayproductdetails'),
    path('userdisplaycart/<int:id>', views.display_cart, name='userdisplaycart'),
    path('addtocart/<int:product_id>/<int:customer_id>/<int:quantity>/<str:range>', views.add_to_cart, name='addtocart'),
    path('updatecartquantity/<int:product_id>/<int:user_id>/<str:method>', views.update_cart_quantity, name='updatecartquantity'),
    path('deletefromcart/<int:id>/<int:userid>', views.delete_from_cart, name='deletefromcart'),
    path('checkout/<int:id>/<str:discount>', views.checkout, name='checkout'),
    path('directcheckout/<str:product_id>/<str:range>/<int:user_id>', views.direct_checkout, name='directcheckout'),
    path('accountdetails/<int:id>', views.account_details, name='accountdetails'),
    path('updateuserdetails/<int:id>', views.update_user_details, name='updateuserdetails'),
    path('updateuserpassword/<int:id>', views.update_user_password, name='updateuserpassword'),
    path('displayaddress/<int:id>', views.display_address, name='displayaddress'),
    path('addaddress/<int:id>/<str:range>', views.add_address, name='addaddress'),
    path('updatedefaultaddress/<int:id>', views.update_default_address, name='updatedefaultaddress'),
    path('updateaddress/<int:id>', views.update_address, name='updateaddress'),
    path('deleteaddress/<int:id>/<int:address_id>', views.delete_address, name='deleteaddress'),
    path('placeorder/<int:id>/<str:final_amount>/<str:coupon_code>/<str:payment_mode>', views.place_order, name='placeorder'),
    path('applycoupon/<int:id>/<str:amount>/<str:payableamount>', views.apply_coupon, name='applycoupon'),
    path('userorders/<int:id>', views.display_orders, name='userorders'),
    path('userorderdetails/<int:order_id>', views.order_details, name='userorderdetails'),
    path('favouriteproduct/<int:user_id>/<int:product_id>/<str:range>', views.favourite_product, name='favouriteproduct'),
    path('displayfavouriteproduct/<int:user_id>', views.display_favourite_product, name='displayfavouriteproduct'),
    path('userorderstatus/<int:order_id>/<str:status>', views.user_order_status, name='userorderstatus'),
    path('searchproduct', views.search_product, name='searchproduct'),
    path('displaywallet/<int:id>', views.display_wallet, name='displaywallet'),
    path('singleorder/<int:order_id>', views.single_order_details, name='singleorder'),
    
]
