from django.db import models

# Create your models here.

class user_info(models.Model):
    # id = models.IntegerField(primary_key=True,auto_created=True)
    name = models.TextField(255)
    email = models.EmailField()
    password = models.CharField(max_length = 16)
    date_created = models.DateTimeField(auto_now=True)
    store_name = models.TextField(max_length=150)

class device_info(models.Model):
    '''
    device_id of each raspberry pi
    '''
    # id = models.IntegerField(primary_key=True,auto_created=True)
    device_id = models.TextField(max_length=14)
    device_label = models.TextField(max_length=50)
    pp_kg = models.FloatField(null=True)
    user_id = models.ForeignKey(user_info,on_delete=models.CASCADE)

class sales_track(models.Model):
    # id = models.IntegerField(primary_key=True,auto_created=True)
    sales = models.FloatField() # KG
    device_id = models.ForeignKey(device_info,on_delete = models.CASCADE)
    date_created = models.DateTimeField(auto_now=True)
