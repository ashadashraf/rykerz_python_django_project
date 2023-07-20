from django.shortcuts import render
from userside.models import BulkOrder, Order
from django.db.models import Sum

from django.http import HttpResponse
# from django.template.loader import get_template
# from xhtml2pdf import pisa
# import pdfkit

# Create your views here.

def order_invoice(request, order_id):
    try:
        if BulkOrder.objects.get(bulk_order=order_id):
            bulk_order = BulkOrder.objects.get(bulk_order=order_id)
            order = Order.objects.filter(bulk_order=order_id).exclude(order_status='cancelled')
    except:
        order = Order.objects.get(id=order_id)
        bulk_order = order.bulk_order
    if bulk_order.coupon:
        if bulk_order.coupon.is_price_based:
            coupon_amount = bulk_order.coupon.discount_price
        else:
            order_total = Order.objects.filter(bulk_order=bulk_order).aggregate(Sum('total_amount'))['total_amount__sum']
            print(order_total)
            coupon_amount = round(order_total * (bulk_order.coupon.discount_percentage / 100), 2)
        total = bulk_order.final_amount + coupon_amount
    else:
        coupon_amount = None
        total = bulk_order.final_amount
    return render(request, 'pdf_convert/show_info.html',{'orders':order, 'bulk_order':bulk_order, 'total':total, 'coupon_amount':coupon_amount})


# def pdf_report_create(request, order_id):
#     try:
#         if BulkOrder.objects.get(bulk_order=order_id):
#             bulk_order = BulkOrder.objects.get(bulk_order=order_id)
#             order = Order.objects.filter(bulk_order=order_id).exclude(order_status='cancelled')
#     except:
#         order = Order.objects.get(id=order_id)
#         bulk_order = order.bulk_order
#     if bulk_order.coupon:
#         if bulk_order.coupon.is_price_based:
#             coupon_amount = bulk_order.coupon.discount_price
#         else:
#             order_total = Order.objects.filter(bulk_order=bulk_order).aggregate(Sum('total_amount'))['total_amount__sum']
#             print(order_total)
#             coupon_amount = round(order_total * (bulk_order.coupon.discount_percentage / 100), 2)
#         total = bulk_order.final_amount + coupon_amount
#     else:
#         coupon_amount = None
#         total = bulk_order.final_amount

#     template_path = 'pdf_convert/pdf_report.html'

#     response = HttpResponse(content_type='application/pdf')
#     # attachment; 
#     response['Content-Disposition'] = 'filename="order_report.pdf"'
#     template = get_template(template_path)
#     html = template.render({'orders':order, 'bulk_order':bulk_order, 'total':total, 'coupon_amount':coupon_amount, 'user':request.user})

#     # create a pdf
#     pisa_status = pisa.CreatePDF(
#        html, dest=response)
#     # if error then show some funny view
#     if pisa_status.err:
#        return HttpResponse('We had some errors <pre>' + html + '</pre>')
#     return response


import csv
from django.http import HttpResponse
from userside.models import Transaction

def sales_report_pdf(request):
    sales_data = Transaction.objects.all()

    # Prepare the response and set the appropriate headers
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'

    # Create a CSV writer
    writer = csv.writer(response)
    
    # Write the header row
    writer.writerow(['Transaction ID', 'Date', 'Amount', 'Status'])  # Customize the headers as needed

    # Write the sales data rows
    for sale in sales_data:
        writer.writerow([sale.id, sale.transaction_date, sale.transaction_amount, sale.transaction_status])  # Customize the data fields as needed

    return response