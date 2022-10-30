from rest_framework.serializers import ModelSerializer
from rest_framework.fields import CharField,ImageField,URLField,BooleanField
from .models import *

class CategorySerializer(ModelSerializer):

    class Meta:
        model=Category
        fields='__all__'


class OfferSerializer(ModelSerializer):
    class Meta:
        model=Offer
        fields='__all__'
class AdditionsSerializer(ModelSerializer):
    class Meta:
        model=Addition
        fields='__all__'
class FoodSerializer(ModelSerializer):


    categoryName=CharField(source='category.name',read_only=True)
    image=ImageField(write_only=True,required=False)
    imageUrl=URLField(source='image.url',read_only=True)
    offer=OfferSerializer(read_only=True)
    additions=AdditionsSerializer(many=True,read_only=True)
    visiblity=BooleanField(read_only=True)
    class Meta:
        model=Food
        fields=['desc','id','offer','additions','points','visiblity',
        'name','price','category','categoryName','imageUrl','image']

    
class AdvertiseSerializer(ModelSerializer):
    image=ImageField(write_only=True,required=False)
    imageUrl=URLField(source='image.url',read_only=True)

    class Meta:
        model=Advertise
        fields=['id','title','subTitle','image','imageUrl','food']


class FoodListSerializer(ModelSerializer):

    class Meta:
        model=Food
        fields=['id','name']