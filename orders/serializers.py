from rest_framework.serializers import ModelSerializer
from rest_framework.fields import URLField,FloatField,CharField
from .models import *
from foods.serializers import OfferSerializer,AdditionsSerializer
from accounts.serializers import LocationSerializer

class _UserSerializer(ModelSerializer):
    name=CharField(source='user.name')
    class Meta: 
        model=ClientUser
        fields=['id','name','phone']
class CouponSerializer(ModelSerializer):

    class Meta:
        model=Coupon
        fields=['key','enabled','value','type','usedBy','id']
class CartItemWriteSerializer(ModelSerializer):
    class Meta:
        model=CartItem
        exclude=['additions','usedPoints']

class CartItemWriteSerializer2(ModelSerializer):
    total=FloatField()
    class Meta:
        model=CartItem
        fields=['freeItems','usedPoints',"food",'count','total','note']

class _FoodSerializer(ModelSerializer):
    offer=OfferSerializer()
    imageUrl=URLField(source='image.url')
    class Meta:
        model=Food
        fields=['name','id','offer','price','points','imageUrl']
class _AdditionSerializer(ModelSerializer):

    class Meta:
        model=Addition
        fields=['name','price']
class CartItemReadSerializer(ModelSerializer):
    food=_FoodSerializer()
    additions=_AdditionSerializer(many=True)
    total=FloatField()
    class Meta:
        model=CartItem
        # fields='__all__'
        fields=['food','id','count','additions','user','freeItems','total','usedPoints','note']

class OrderItemReadSerializer(ModelSerializer):
    food=_FoodSerializer()
    additions=AdditionsSerializer(many=True)
    class Meta:
        model=OrderItem
        exclude=['order']

class OrderItemWriteSerializer(ModelSerializer):
    class Meta:
        model=OrderItem
        exclude=['order','additions']

class OrderReadSerializer(ModelSerializer):
    items=OrderItemReadSerializer(many=True,source='items.all')
    total=FloatField()
    user=_UserSerializer()
    location=LocationSerializer()
    coupon=CouponSerializer()
    class Meta:
        model=Order
        fields="__all__"

class OrderWriteSerilizer(ModelSerializer):

    class Meta:
        model=Order
        fields=['payMethod','recieveTime','location']
