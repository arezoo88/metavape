from django.contrib import admin
from product import models


admin.site.register(models.Shop)
admin.site.register(models.Product)
admin.site.register(models.Rating)
admin.site.register(models.Comment)
admin.site.register(models.Favorite)
admin.site.register(models.ImageList)
admin.site.register(models.ProductImage)