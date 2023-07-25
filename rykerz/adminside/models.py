from django.db import models

# Create your models here.

class Category(models.Model):
    category_name = models.CharField(primary_key=True, max_length=30, unique=True)
    category_status = models.BooleanField(default=True)

    def __str__(self):
        return self.category_name
    
class SubCategory(models.Model):
    category = models.ForeignKey(Category, null=False, on_delete=models.CASCADE)
    sub_category_name = models.CharField(max_length=30)
    sub_category_image = models.ImageField(upload_to="product/images", null=False, blank=False)
    sub_category_status = models.BooleanField(default=True)

    def __str__(self):
        return self.sub_category_name
    
    
class ProductImage(models.Model):
    image1 = models.ImageField(upload_to="product/images", null=False, blank=False)
    image2 = models.ImageField(upload_to="product/images", null=False, blank=False)
    image3 = models.ImageField(upload_to="product/images", null=False, blank=False)

    
class Product(models.Model):
    product_name= models.CharField(max_length=30, unique=True)
    product_category = models.ForeignKey(Category, null=False, on_delete=models.CASCADE)
    product_sub_category = models.ForeignKey(SubCategory, null=False, on_delete=models.CASCADE)
    product_label = models.CharField(max_length=45)
    product_description = models.TextField()
    product_status = models.BooleanField(default=False)
    product_image_id = models.OneToOneField(ProductImage, null=False, on_delete=models.CASCADE)
    product_price = models.FloatField()
    sales_price = models.FloatField()
    product_tax = models.FloatField()
    profit_margin = models.FloatField()
    stock = models.IntegerField()
    unit = models.BooleanField(default=True)
    # unit = True, piece
    # unit = False, weight
    piece = models.IntegerField(blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    duration = models.DurationField()
    total_energy = models.FloatField()
    carbohydrate = models.FloatField()
    fat = models.FloatField()
    protein = models.FloatField()

    offer_price =models.FloatField(null=True)
    expiry_date = models.DateField(null=True)

    # USERNAME_FIELD = 'product_name'
    REQUIRED_FIELDS = ['product_name','product_category','product_status','product_image_id',
                       'product_price','sales_price','profit_margin','stock']

    def __str__(self):
        return self.product_name
    
    def save(self, *args, **kwargs):
        if isinstance(self.sales_price, str):
            self.sales_price = float(self.sales_price)
        if isinstance(self.product_price, str):
            self.product_price = float(self.product_price)
        if isinstance(self.profit_margin, str):
            self.profit_margin = float(self.profit_margin)
        if isinstance(self.total_energy, str):
            self.total_energy = float(self.total_energy)
        if isinstance(self.carbohydrate, str):
            self.carbohydrate = float(self.carbohydrate)
        if isinstance(self.fat, str):
            self.fat = float(self.fat)
        if isinstance(self.protein, str):
            self.protein = float(self.protein)
        if isinstance(self.product_tax, str):
            self.product_tax = float(self.product_tax)
        
        self.sales_price = (self.product_price + (self.product_price * self.profit_margin/100)) + ((self.product_price + (self.product_price * self.profit_margin/100)) * (self.product_tax/100))
        if self.product_price: self.product_price = round(self.product_price, 2)
        if self.sales_price: self.sales_price = round(self.sales_price, 2)
        if self.product_tax: self.product_tax = round(self.product_tax, 2)
        if self.profit_margin: self.profit_margin = round(self.profit_margin, 2)
        if self.offer_price: self.offer_price = round(self.offer_price, 2)
        if self.total_energy: self.total_energy = round(self.total_energy, 2)
        if self.carbohydrate: self.carbohydrate = round(self.carbohydrate, 2)
        if self.fat: self.fat = round(self.fat, 2)
        if self.protein: self.protein = round(self.protein, 2)
        super(Product, self).save(*args, **kwargs)