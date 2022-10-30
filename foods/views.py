from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin,UpdateModelMixin,CreateModelMixin,DestroyModelMixin,RetrieveModelMixin
from rest_framework.exceptions import MethodNotAllowed,ValidationError
from .serializers import *
from django.shortcuts import get_object_or_404
from orders.models import OrderItem
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from util.authentection import TokenAuth
from util.permissions import IClient
class CategoryUserView(GenericAPIView,ListModelMixin):

    serializer_class=CategorySerializer
    queryset=Category.objects.filter(visiblity=True)

    def get(self,request,*arg,**kwargs):
        return self.list(request,*arg,**kwargs)
  
class CategoryView(GenericAPIView,ListModelMixin,UpdateModelMixin,CreateModelMixin,DestroyModelMixin):

    serializer_class=CategorySerializer
    queryset=Category.objects.all()

    def get(self,request,*arg,**kwargs):
        return self.list(request,*arg,**kwargs)
  
  
    def post(self,request,*arg,**kwargs):
        return self.create(request,*arg,**kwargs)
  

    def put(self,request,*arg,**kwargs):
        if not 'pk' in kwargs:
            raise MethodNotAllowed(method="PUT") 
        return self.update(request,*arg,**kwargs)
  
  
    def delete(self,request,*arg,**kwargs):
        if not 'pk' in kwargs:
            raise MethodNotAllowed(method="DELETE")
        return self.destroy(request,*arg,**kwargs)

class FoodUserView(APIView):
    authentication_classes=[TokenAuth]
    permission_classes=[IClient]
    def get(self,request,pk,*args,**kwargs):
        food=get_object_or_404(Food,id=pk)
        serializered=FoodSerializer(instance=food)       
        data=serializered.data
        data['fav']=request.user.client.favorites.filter(id=pk).exists()
        data['userPoints']=request.user.client.points
        return Response(data=data)
class FoodView(GenericAPIView,RetrieveModelMixin,CreateModelMixin,UpdateModelMixin,DestroyModelMixin):
    serializer_class=FoodSerializer
    queryset=Food.objects.all()
    
    def get(self,request,*args,**kwargs):
        if not 'pk' in kwargs:
            raise MethodNotAllowed(method="GET") 
        return self.retrieve(request,*args,**kwargs)



    def post(self,request,*args,**kwargs):
        
        return self.create(request,*args,**kwargs)
       
    def put(self,request,*arg,**kwargs):
      

        if not 'pk' in kwargs:
          raise MethodNotAllowed(method="PUT") 
            
        return self.update(request,*arg,**kwargs)
  
  
    def delete(self,request,*arg,**kwargs):
        if not 'pk' in kwargs:
            raise MethodNotAllowed(method="DELETE")
        return self.destroy(request,*arg,**kwargs)


class CategoryFoodView(GenericAPIView,ListModelMixin):

    serializer_class=FoodSerializer
    queryset=Food.objects.all()

    def filter_queryset(self, queryset):
        queryset=queryset.filter(category_id=self.kwargs['category'])
        return queryset[10*(self.kwargs['page']-1):10*(self.kwargs['page'])]

    def get(self,request,*args,**kwargs):
        return self.list(request,*args,**kwargs)




class AdditionView(GenericAPIView,CreateModelMixin,DestroyModelMixin):
    serializer_class=AdditionsSerializer
    queryset=Addition.objects.all()

    def post(self,request,*args,**kwargs):
        return self.create(request,*args,**kwargs)

    def delete(self,request,*args,**kwargs):
        if not 'pk' in kwargs:
            raise MethodNotAllowed(method="DELETE") 

        return self.destroy(request,*args,**kwargs)

class TopsOfWeekView(GenericAPIView,ListModelMixin):
    serializer_class=FoodSerializer


    def get_queryset(self):
        weekAgo=(timezone.now()-timedelta(days=7)).date()
        qs= OrderItem.objects.filter(food__category__visiblity=True,food__visiblity=True,order__time__date__gte=weekAgo).values('food').annotate(total=Count('food')).order_by('-total')[:25]
        fodIs=list(map(lambda e:e['food'],qs))
        foods=[]
        for id in fodIs:
            foods.append(Food.objects.get(pk=id))
        return foods

    def get(self,request):
        return self.list(request)


class UsersPointsFoodView(APIView):

    authentication_classes=[TokenAuth]
    permission_classes=[IClient]
    def get_queryset(self):
        return Food.objects.filter(category__visiblity=True,visiblity=True,points__lte=self.request.user.client.points)[:30]

    def get(self,request):
        foods=FoodSerializer(instance=self.get_queryset(),many=True)
        data={
            "foods":foods.data,
            'points':request.user.client.points
        }
        return Response(data)






@api_view(['POST'])
def addOffer(request):
    
    
    food=Food.objects.get(pk=request.data['food'])
    if hasattr(food,'offer'):
        food.offer.delete()
    serializered=OfferSerializer(data=request.data)
    if serializered.is_valid(raise_exception=True):
       
        serializered.save()
        return Response(serializered.data,status=201)

@api_view(['POST'])
def addAdditionsToFood(request):
    if 'additions' in request.data:
        print(request.data)
        additions=AdditionsSerializer(data=request.data['additions'],many=True)
        if additions.is_valid():
            additions.save()
            return Response('done',status=201)
        print(additions.errors)
        raise MethodNotAllowed('POST')

@api_view(['PUT'])
def changeCategoryVisible(request,pk):

    category= get_object_or_404(Category,id=pk)
    if 'value' in request.data:
        category.visiblity=request.data['value']
        print(category.visiblity,category.name)
        category.save()
        return Response()
    else:
        raise ValidationError('value required')

class FoodsMenuView(GenericAPIView,ListModelMixin):
    serializer_class=FoodSerializer
    queryset=Food.objects.filter(visiblity=True,category__visiblity=True)

    def filter_queryset(self, queryset):
        if 'offers' in self.request.path:
            queryset=queryset.exclude(offer=None,).filter(offer__end__gte=timezone.now())
            
        if 'points' in self.request.path:
            queryset=queryset.exclude(points=None,)
        if 'category' in  self.request.GET and  not int(self.request.GET['category'])==-1:
             queryset=queryset.filter(category_id= self.request.GET['category'])
        if 'name' in  self.request.GET and  not self.request.GET['name']=='':
            queryset=queryset.filter(name__contains=self.request.GET['name'])
        print(len(queryset))
        return queryset[20*(self.kwargs['page']-1):20*self.kwargs['page']]

    def get(self,request,*args,**kwargs):
        return self.list(request,*args,**kwargs)
class UserFavoriteFoodsView(GenericAPIView,ListModelMixin):
    serializer_class=FoodSerializer
    authentication_classes=[TokenAuth]
    permission_classes=[IClient]

    def get_queryset(self):
        return self.request.user.client.favorites.filter(visiblity=True,category__visiblity=True)[20*(self.kwargs['page']-1):20*self.kwargs['page']]

    def get(self,request,*args,**kwargs):
        return self.list(request)
        
class AdvertiseAdminView(GenericAPIView,CreateModelMixin,ListModelMixin,DestroyModelMixin):

    serializer_class=AdvertiseSerializer
    queryset=Advertise.objects.filter()
    def post(self,request,*args,**kwargs):
        return self.create(request)

    def get(self,request,*args,**kwargs):
        return self.list(request)

    def delete(self,request,*args,**kwargs):
        return self.destroy(request,*args,**kwargs)
        
class AdvertiseView(GenericAPIView,ListModelMixin):

    serializer_class=AdvertiseSerializer
    queryset=Advertise.objects.filter(food__category__visiblity=True,food__visiblity=True)

    def get(self,request,*args,**kwargs):
        return self.list(request)
@api_view(['PUT'])
def changeFoodVisible(request,pk):
    food= get_object_or_404(Food,id=pk)
    if 'value' in request.data:
        food.visiblity=request.data['value']
        food.save()
        return Response()
    else:
        raise ValidationError('value required')


class AllFoodView(GenericAPIView,ListModelMixin):
    serializer_class=FoodListSerializer
    queryset=Food.objects.all().order_by('name')

    def get(self,request):
        return self.list(request)