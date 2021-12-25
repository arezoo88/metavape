from django.db import models

class BaseModel(models.Model): #other models use this model and inherit from this
    created_date = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    modified_date = models.DateTimeField(auto_now=True,null=True,blank=True)
    enabled = models.BooleanField(default=True)
    class Meta:
        abstract = True