from django.urls import path
from adminside import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('dashboard',views.base, name='dashboard'),
    path('index', views.index, name='index'),
    path('d-products', views.display_products, name='d-products'),
    path('add-product', views.add_product, name='add-product'),
    path('u-product/<int:id>', views.update, name='u-product'),
    path('productsubcategoryupdate/<str:category>', views.product_subcategory_update, name='productsubcategoryupdate'),
    path('u-product-record/<int:id>', views.update_product, name='u-product-record'),
    path('u-product-status/<int:id>', views.update_status, name='u-product-status'),
    path('updateproductstock', views.update_product_stock, name='updateproductstock'),
    path('product-details/<int:id>', views.product_details, name='product-details'),
    path('d-category', views.display_category, name='d-category'),
    path('add-category', views.add_category, name='add-category'),
    path('u-category/<str:name>', views.update_category, name='u-category'),
    path('u-category-record/<str:name>', views.update_category_record, name='u-category-record'),
    path('u-category-status/<str:name>', views.update_category_status, name='u-category-status'),
    path('category-details/<str:name>', views.category_details, name='category_details'),
    path('d-sub-category/<str:c_name>', views.display_sub_category, name='d-sub-category'),
    path('add-sub-category', views.add_sub_category, name='add-sub-category'),
    path('u-sub-category/<str:category_name>/<str:subcategory_name>', views.update_sub_category, name='u-sub-category'),
    path('u-sub-category-record/<str:category_name>/<str:subcategory_name>', views.update_sub_category_record, name='u-sub-category-record'),
    path('u-sub-category-status/<str:category_name>/<str:subcategory_name>', views.update_sub_category_status, name='u-sub-category-status'),
    path('d-user', views.display_user, name='d-user'),
    path('user-details/<str:name>', views.user_details, name='user-details'),
    path('u-user-status/<str:name>', views.update_user_status, name='u-user-status'),
    path('displaycoupon', views.display_coupon, name='displaycoupon'),
    path('addcoupon', views.add_coupon, name='addcoupon'),
    path('displayorders', views.display_orders, name='displayorders'),
    path('updateorderstatus/<int:order_id>/<str:status>', views.update_order_status, name='updateorderstatus'),
    path('displayoffers', views.display_offers, name='displayoffers'),
    path('addoffer/<int:id>', views.add_offer, name='addoffer'),
    path('displayorderdetails/<int:order_id>', views.display_order_details, name='displayorderdetails'),
    path('removeoffer/<int:id>', views.remove_offer, name='removeoffer'),
    path('displaytransactions', views.display_transactions, name='displaytransactions'),
    path('adminsidesearch/<str:range>/<str:subrange>', views.adminside_search, name='adminsidesearch'),
    path('displaybestsellers', views.display_bestsellers, name='displaybestsellers'),
    path('addbestsellers/<str:category>', views.add_bestsellers, name='addbestsellers'),
    path('removebestsellers/<str:product>/<str:category>', views.remove_bestsellers, name='removebestsellers'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)