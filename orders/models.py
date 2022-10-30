from django.db import models
from accounts.models import ClientUser, Location
from foods.models import Food,Addition
class Coupon(models.Model):
    types=[
        ('p','Percent'),
        ('c','Cash'),
    ]
    key=models.CharField(max_length=50,unique=True)
    enabled=models.BooleanField(default=True)
    value=models.PositiveIntegerField()
    type=models.CharField(max_length=1,choices=types)
    class Types:
        percent='p'
        cash='c'

    def usedBy(self): 
        return Order.objects.filter(coupon=self).count()
class __Item(models.Model):
    freeItems=models.PositiveIntegerField(default=0)
    usedPoints=models.PositiveIntegerField(default=0)
    food=models.ForeignKey(Food,on_delete=models.CASCADE)
    count=models.PositiveSmallIntegerField()
    additions=models.ManyToManyField(Addition)
    note=models.TextField(blank=True)
    
    class Meta:
        abstract=True

class Order(models.Model):
    states=[
        ('r','rejected'),
        ('c','cooking'),
        ('q','in queue'),
        ('w','waiting'),
        ('d','delivering'),
        ('f','finshed'),
        ('t','terminate'),

    ]
    payMethods=[
        ('ca','cash'),
        ('cc','card'),
        ('rs','recieve from store'),
    ]
 
    user=models.ForeignKey(ClientUser,on_delete=models.CASCADE)
    status=models.CharField(max_length=1,choices=states)
  
    payMethod=models.CharField(max_length=2,choices=payMethods)
    recieveTime=models.TimeField(null=True)
    coupon=models.ForeignKey(Coupon,on_delete=models.SET_NULL,null=True)
    location=models.ForeignKey(Location,on_delete=models.CASCADE)
    time=models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together=['user','coupon']
    class PayMethods:
        cash='ca'
        card='cc'

 
    class States:
        rejected='r'
        cooking='c'
        inQueue='q'
        waiting='w'
        delivering='d'
        finshed='f'
        terminate='t'
    def total(self):
        total=0
        for item in self.items.all():
            total+=item.total
        if not self.coupon==None:
            if self.coupon.type==Coupon.Types.percent:
               total=total-(total*self.coupon.value/100)
            elif self.coupon.type==Coupon.Types.cash:
                total=total-self.coupon.value
                total=total if total >=0 else 0
        return total
class CartItem(__Item):
    user=models.ForeignKey(ClientUser,on_delete=models.CASCADE)

    class Types:
        free='f'
        paid='p'

class OrderItem(__Item):
    order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name='items')
    total=models.FloatField()
