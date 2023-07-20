from django.urls import path
from pdf_convert import views

urlpatterns = [
    path('orderinvoice/<str:order_id>', views.order_invoice, name='orderinvoice'),
    # path('createpdf/<str:order_id>', views.pdf_report_create, name='createpdf'),
    path('salesreportpdf', views.sales_report_pdf, name='salesreportpdf'),
    # path('generate_pdf/<str:order_id>', views.generate_pdf, name='generate_pdf'),
]