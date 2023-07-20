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
    



