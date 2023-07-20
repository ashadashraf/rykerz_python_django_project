from django.db import models
from adminside.models import Product, Category
from authentication.models import CustomUser
import uuid
from decimal import Decimal

# Create your models here.

class Cart(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False)
    quantity = models.IntegerField()
    unit_price = models.FloatField()
    total_price = models.FloatField()
    selected = models.BooleanField(default=False)

class Favourites(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False)
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False)

class InstantBuy(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False)
    quantity = models.IntegerField()
    unit_price = models.FloatField()
    total_price = models.FloatField()
    selected = models.BooleanField(default=False)

class Address(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False)
    address_name = models.CharField(max_length=30)
    full_name = models.CharField(max_length=20)
    mobile = models.CharField(max_length=30)
    pincode = models.IntegerField()
    building = models.CharField(max_length=50)
    area = models.CharField(max_length=50)
    landmark = models.CharField(max_length=50)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=15)
    active_address = models.BooleanField(default=False)

class Coupon(models.Model):
    coupon_code = models.CharField(max_length=15, unique=True)
    created_date = models.DateField(auto_now_add=True)
    expiry_date = models.DateField()
    is_price_based = models.BooleanField(default=False)
    discount_price = models.FloatField(default=0.0)
    discount_percentage = models.FloatField(default=0.0)
    min_purchase = models.FloatField(null=False)


class BulkOrder(models.Model):
    bulk_order = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False, unique=True)
    date = models.DateTimeField(auto_now_add=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, null=True)
    address = models.ForeignKey(Address, on_delete=models.PROTECT, null=False)
    payment_status = models.BooleanField(default=False)
    final_amount = models.FloatField(null=True)
    delivery_charge = models.FloatField(default=20, null=True)
    delivery_date = models.DateTimeField(auto_now_add=True)
    tax_rate = models.FloatField(default=5/100)
    tax_amount = models.FloatField(null=True)

    def save(self, *args, **kwargs):
        if isinstance(self.final_amount, str):
            self.final_amount = float(self.final_amount)
        elif isinstance(self.final_amount, Decimal):
            self.final_amount = float(self.final_amount)

        if isinstance(self.final_amount, (int, float)):
            self.tax_amount = (self.final_amount - self.delivery_charge) * self.tax_rate
        else:
            self.tax_amount = None
        super(BulkOrder, self).save(*args, **kwargs)


class Order(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False)
    quantity = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(max_length=30)
    payment_status = models.BooleanField(default=False)
    amount = models.FloatField()
    bulk_order = models.ForeignKey(BulkOrder, on_delete=models.CASCADE, null=False)
    tax_rate = models.FloatField(default=5/100)
    tax_amount = models.FloatField(null=True)
    total_amount = models.IntegerField(null=True)

    def save(self, *args, **kwargs):
        self.total_amount = self.product.sales_price * self.quantity
        print(self.tax_rate, self.product.product_price, self.quantity)
        self.tax_amount = self.tax_rate * (self.product.product_price * self.quantity)
        self.tax_amount = round(self.tax_amount, 2)
        self.amount = self.total_amount - self.tax_amount
        super(Order, self).save(*args, **kwargs)
  

class Wallet(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False)
    amount = models.FloatField()


class Transaction(models.Model):
    bulk_order = models.ForeignKey(BulkOrder, on_delete=models.CASCADE, null=True)
    transaction_mode = models.CharField(max_length=50, default=None)
    payment_gateway_id = models.CharField(default=None, null=True)
    transaction_amount = models.FloatField()
    transaction_date = models.DateTimeField()
    transaction_status = models.CharField(default=False, max_length=20)
