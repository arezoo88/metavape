from django.db import models
from cloudinary.models import CloudinaryField
from django.contrib.auth import get_user_model
from utils.models import BaseModel
from django.core.validators import MaxValueValidator

User = get_user_model()
class Shop(models.Model):
    name = models.CharField(max_length=100)
    nam_xpath = models.CharField(max_length=1000,blank=True)
    description_xpath = models.CharField(max_length=1000,blank=True)
    star_xpath = models.CharField(max_length=1000,blank=True)
    rating_nember_xpath = models.CharField(max_length=1000,blank=True)
    title_xpath = models.CharField(max_length=1000,blank=True)
    comment_xpath = models.CharField(max_length=1000,blank=True)
    image_xpath = models.CharField(max_length=1000,blank=True)

class Product(models.Model):
    id = models.CharField(
        primary_key=True, editable=False, max_length=30)
    name = models.CharField(max_length=200)
    description = models.TextField()
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    image =  models.ForeignKey('ImageList',related_name='product',on_delete=models.CASCADE,blank=True,null=True)
    product_url = models.CharField(max_length=1000,null=True,blank=True)
class ProductImage(models.Model):
    parent = models.ForeignKey(to='ImageList', on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField('image', folder="liquids/")


class ImageList(models.Model):
    id = models.CharField(
        primary_key=True, editable=False, max_length=30)

class Comment(BaseModel):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    shop = models.ForeignKey(Shop,on_delete=models.CASCADE,null=True,blank=True)
    body = models.TextField(null=True,blank=True)
    title = models.CharField(max_length=500,null=True,blank=True)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    class Meta:
        ordering = ['created_date']
    
    def __str__(self):
        return 'Comment {} by {}'.format(self.body, self.user.email)

class Rating(BaseModel):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    shop = models.ForeignKey(Shop,on_delete=models.CASCADE,null=True,blank=True)
    rating_number = models.IntegerField(null=True,blank=True)
    star = models.PositiveSmallIntegerField(validators=[MaxValueValidator(5)], default=0)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.star} - {self.product}"
    
class Favorite(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    

