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
    def save(self, *args, **kwargs):
        if isinstance(self.unit_price, str):
            self.unit_price = float(self.unit_price)
        if isinstance(self.total_price, str):
            self.total_price = float(self.total_price)
        self.unit_price = round(self.unit_price, 2)
        self.total_price = round(self.total_price, 2)
        super(Cart, self).save(*args, **kwargs)

class Favourites(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False)
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False)

class BestSellers(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=False)

class InstantBuy(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False)
    quantity = models.IntegerField()
    unit_price = models.FloatField()
    total_price = models.FloatField()
    selected = models.BooleanField(default=False)
    def save(self, *args, **kwargs):
        if isinstance(self.unit_price, str):
            self.unit_price = float(self.unit_price)
        if isinstance(self.total_price, str):
            self.total_price = float(self.total_price)
        self.unit_price = round(self.unit_price, 2)
        self.total_price = round(self.total_price, 2)
        super(InstantBuy, self).save(*args, **kwargs)

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
    def save(self, *args, **kwargs):
        if isinstance(self.discount_price, str):
            self.discount_price = float(self.discount_price)
        if isinstance(self.discount_percentage, str):
            self.discount_percentage = float(self.discount_percentage)
        self.discount_price = round(self.discount_price, 2)
        self.discount_percentage = round(self.discount_percentage, 2)
        super(Coupon, self).save(*args, **kwargs)


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
        if isinstance(self.delivery_charge, str):
            self.delivery_charge = float(self.delivery_charge)
        if isinstance(self.tax_rate, str):
            self.tax_rate = float(self.tax_rate)
        if self.final_amount:
            self.final_amount = round(self.final_amount, 2)
        else:
            self.delivery_charge = 0
        if self.delivery_charge:
            self.delivery_charge = round(self.delivery_charge, 2)
        if self.tax_rate:
            self.tax_rate = round(self.tax_rate, 2)
        if self.tax_amount:
            self.tax_amount = round(self.tax_amount, 2)
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
        self.tax_rate = round(self.product.product_tax, 2)
        # if self.product.offer_price:
        #     self.tax_amount = (self.tax_rate/100) * (self.product.offer_price * self.quantity)
        # else:
        self.tax_amount = (self.tax_rate/100) * (self.product.product_price + (self.product.product_price*(self.product.profit_margin/100)))
        self.tax_amount = round(self.tax_amount, 2)
        self.total_amount = round(self.total_amount, 2)
        self.amount = round(self.amount, 2)
        super(Order, self).save(*args, **kwargs)
  

class Wallet(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False)
    amount = models.FloatField()
    def save(self, *args, **kwargs):
        self.amount = round(self.amount, 2)
        super(Wallet, self).save(*args, **kwargs)


class Transaction(models.Model):
    bulk_order = models.ForeignKey(BulkOrder, on_delete=models.CASCADE, null=True)
    transaction_mode = models.CharField(max_length=50, default=None)
    payment_gateway_id = models.CharField(default=None, null=True)
    transaction_amount = models.FloatField()
    transaction_date = models.DateTimeField()
    transaction_status = models.CharField(default=False, max_length=20)
    def save(self, *args, **kwargs):
        self.transaction_amount = round(self.transaction_amount, 2)
        super(Transaction, self).save(*args, **kwargs)