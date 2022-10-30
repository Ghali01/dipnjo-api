from django.db import models


class Category(models.Model):
    name=models.CharField(max_length=100)
    visiblity=models.BooleanField(default=True)


class Food(models.Model):
    name=models.CharField(max_length=100)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    visiblity=models.BooleanField(default=True)
    price=models.FloatField()
    desc=models.TextField(blank=True)
    image=models.ImageField(upload_to='foods/')
    points=models.PositiveIntegerField(null=True)    
class Addition(models.Model):
    food=models.ForeignKey(Food,on_delete=models.CASCADE,related_name='additions')
    name=models.CharField(max_length=255)
    price=models.FloatField()

class Offer(models.Model):
    types=[
        ("1","Precent"),
        ("2","New Price"),
    ]
    type=models.CharField(max_length=1,choices=types)
    value=models.FloatField()
    start=models.DateTimeField(auto_now_add=True)
    end=models.DateTimeField()
    food=models.OneToOneField(Food,on_delete=models.CASCADE,related_name='offer')


    class Types:
        precent='1'
        newPrice='2'

class Advertise(models.Model):
    title=models.CharField(max_length=30)
    subTitle=models.CharField(max_length=60)
    image=models.ImageField(upload_to='advertises/')
    food=models.ForeignKey(Food,on_delete=models.CASCADE)