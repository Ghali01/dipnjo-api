from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from firebase_admin import messaging

from foods.models import Food
class UserManager(BaseUserManager):

    def create_user(self,token,name,password=None):
        user=User(token=token,name=name,password=password)
        user.set_password(password)
        user.save()
        return user
    def create_superuser(self,token,name,password=None):
        user=self.create_user(token=token,name=name,password=password)
        user.is_staff=True
        user.save()

class User(AbstractBaseUser):
    token=models.CharField(max_length=255,unique=True)
    fcmToken=models.CharField(max_length=255)
    name=models.CharField(max_length=100)
    is_staff=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)
    USERNAME_FIELD='token'
    EMAILFIELD='name'
    REQUIRED_FIELDS=['name']
    objects=UserManager()
    def has_perm(self,perm,obj=None):
        return self.is_staff

    def has_module_perms(self,app_label):
        return True

class ClientUser(models.Model):
    genders=[
        ('m','Male'),
        ('f','Female'),
    ]
    rates=[
        (None,'none'),
        (1,'1'),
        (2,'2'),
        (3,'3'),
        (4,'4'),
        (5,'5'),
        ]
    email=models.EmailField(null=True)
    phone=models.CharField(max_length=20,null=True)
    gender=models.CharField(max_length=1,choices=genders)
    birth=models.DateField()
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='client')
    points=models.PositiveIntegerField(default=0)
    favorites=models.ManyToManyField(Food)
    shareCodeValidated=models.BooleanField(default=False)
    usersSharedCount=models.PositiveIntegerField(default=0)
    rate=models.PositiveIntegerField(null=True,choices=rates)
    def subcicribeTopics(self):
        token=[self.user.fcmToken]
        messaging.subscribe_to_topic(token,f'b-{self.birth.year}')
        messaging.subscribe_to_topic(token,'user')

    def __str__(self) -> str:
        return self.user.name        
class Location(models.Model):
    name=models.CharField(max_length=100)
    details=models.CharField(max_length=255)
    lat=models.DecimalField(max_digits=15, decimal_places=12)
    lng=models.DecimalField(max_digits=15, decimal_places=12)
    user=models.ForeignKey(ClientUser,on_delete=models.CASCADE,related_name='locations')
