import re
from django.db.models import F,Q,Sum
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin,DestroyModelMixin,ListModelMixin,RetrieveModelMixin
from foods.models import Offer
from util.noitfication import NotificationTypes
from .serializers import *
from rest_framework.exceptions import MethodNotAllowed,ValidationError,PermissionDenied,NotAcceptable
from util.authentection import TokenAuth
from util.permissions import IClient
from django.utils import timezone
from django.shortcuts import get_object_or_404
from firebase_admin import messaging
class CartItemView(GenericAPIView,DestroyModelMixin):
    serializer_class=CartItemWriteSerializer
    queryset=CartItem.objects.all()
    authentication_classes=[TokenAuth]
    permission_classes=[IClient]

    def post(self,request,*args,**kwargs):
        user=request.user.client
        request.data['user']=user.id
        serailizered=CartItemWriteSerializer(data=request.data)
        if serailizered.is_valid(raise_exception=True):
            food =Food.objects.get(pk=request.data['food'])
            if user.points>= (request.data['freeItems']*(food.points or 0)):
                user.points=F('points')-(request.data['freeItems'] * (food.points or 0))
                user.save()
                serailizered.save(usedPoints=request.data['freeItems']*(food.points or 0))
          
                if 'additions' in request.data:
                    for id in request.data['additions']:
                        serailizered.instance.additions.add(Addition.objects.get(pk=id))        
                return Response(serailizered.data,status=201)
            raise NotAcceptable()

    def delete(self,request,*args,**kwargs):
        if not 'pk' in kwargs:
            raise MethodNotAllowed(method="DELETE") 
        item=get_object_or_404(CartItem,id=kwargs['pk'])
        if item.user==request.user.client:
            user=request.user.client
            dPoints= item.usedPoints
            item.delete()
            user.points=F('points')+dPoints
            user.save()
            return Response('',status=204)
        raise PermissionDenied("not your item")

class UserCartView(APIView):
    
    authentication_classes=[TokenAuth]
    permission_classes=[IClient]
   
    def get(self,request,*args,**kwargs):
        items= CartItem.objects.filter(user=request.user.client)
        for item in items:
            food=item.food
            total=0
            if hasattr(item.food,'offer') and food.offer.start<timezone.now() and food.offer.end>timezone.now():
                offer=food.offer
                if offer.type==Offer.Types.newPrice:
                    total=(offer.value)*(item.count-item.freeItems)
                elif offer.type==Offer.Types.precent:
                    total=(food.price-(food.price*offer.value/100))*(item.count-item.freeItems)
        
            else:
                total=food.price*(item.count-item.freeItems)
            for addition in item.additions.all():
                total+=addition.price*item.count
            item.total=total
        serializered=CartItemReadSerializer(items,many=True)
        return Response(serializered.data)

    def delete(self,request):
        items= CartItem.objects.filter(user=request.user.client)
        dPoints= 0
        for item in items:
            dPoints+=item.usedPoints
        items.delete()
        user=request.user.client
        user.points=F('points')+dPoints
        user.save()
        return Response('',status=204)
class SendOrederView(APIView):
    
    authentication_classes=[TokenAuth]
    permission_classes=[IClient]
    
    def post(self,request):
        serializered=OrderWriteSerilizer(data=request.data)
        if serializered.is_valid(raise_exception=True):
            coupon=None
            if 'promoCode' in request.data and not request.data['promoCode']==None:
                coupon=get_object_or_404(Coupon,key=request.data['promoCode'])
            serializered.save(status=Order.States.inQueue,user=request.user.client,coupon=coupon)
            items= CartItem.objects.filter(user=request.user.client)
            for item in items:
                food=item.food
                total=0
                if hasattr(item.food,'offer') and food.offer.start<timezone.now() and food.offer.end>timezone.now():
                    offer=food.offer
                    if offer.type==Offer.Types.newPrice:
                        total=(offer.value)*(item.count-item.freeItems)
                    elif offer.type==Offer.Types.precent:
                        total=(food.price-(food.price*offer.value/100))*(item.count-item.freeItems)
            
                else:
                    total=food.price*(item.count-item.freeItems)
                for addition in item.additions.all():
                    total+=addition.price*item.count
                item.total=total
                cartItemSeri=CartItemWriteSerializer2(instance=item)
           
                orderItemSeri=OrderItemWriteSerializer(data=cartItemSeri.data)
                orderItemSeri.is_valid()
                orderItemSeri.save(order=serializered.instance)
                for addition in item.additions.all():
                    orderItemSeri.instance.additions.add(addition)
            items.delete()
            orderData=OrderReadSerializer(instance=serializered.instance).data
            msg=messaging.Message(
                notification=messaging.Notification(
                    title='New Order',
                    body='there is new order'
                ),
                data={
                    'type':str(NotificationTypes.newOrder),
                    'id':str(orderData['id'])
                },
                topic='admin'

            )
            r=messaging.send(msg)
            return Response(orderData,status=201)


class OrdersView(GenericAPIView,ListModelMixin):
    serializer_class=OrderReadSerializer
    queryset=Order.objects.all().order_by('-time')
    

    def filter_queryset(self, queryset):
        if 'status' in self.request.GET:
            queryset=queryset.filter(status=self.request.GET['status'])
        
        if 'payMethod' in self.request.GET:
            queryset=queryset.filter(payMethod=self.request.GET['payMethod'])
        
        queryset=queryset[20*(self.kwargs['page']-1):20*(self.kwargs['page'])]
        return queryset

    def get(self,request,*args,**kwargs):
        return self.list(request,*args,**kwargs)

class OrderView(GenericAPIView,RetrieveModelMixin):
    serializer_class=OrderReadSerializer
    queryset=Order.objects.all()

    def get(self, request,*args,**kwargs):
        return self.retrieve(request,*args,**kwargs)

@api_view(['PUT'])
def setOrderStatus(request):
    if 'id' in request.data and 'status' in request.data:
        order=get_object_or_404(Order,id=request.data['id'])
        order.status=request.data['status']
        order.save()
        if order.status== Order.States.finshed:
            points=0 
            for item in order.items.all():
                points+=(item.food.points or 0)*(item.count-item.freeItems)
            order.user.points=F('points')+int(points*0.1)
            order.user.save()
           
        
        if not order.status== Order.States.finshed:
            registration_token = order.user.user.fcmToken

            message = messaging.Message(
                data={
                    'type': str(NotificationTypes.orderStatus),
                    'order_id': str(order.id),
                    'status':order.status
                },
                token=registration_token,
            )

            response = messaging.send(message)
            
        return Response()
    raise ValidationError()

class CouponView(GenericAPIView,CreateModelMixin,ListModelMixin):
    serializer_class=CouponSerializer
    queryset=Coupon.objects.all()

    def filter_queryset(self, queryset):
        if 'key' in self.request.GET  and not self.request.GET['key']=='':
            queryset=queryset.filter(key__startswith=self.request.GET['key'])
        queryset=queryset[25*(self.kwargs['page']-1):25*(self.kwargs['page'])]
        return queryset

    def get(self,request,*args,**kwargs):
        return self.list(request,*args,**kwargs)
    
    def post(self,request,*args,**kwargs):
        return self.create(request,*args,**kwargs)

    def put(self,request,pk,*args,**kwargs):
        coupon=get_object_or_404(Coupon,id=pk)
        if 'value' in request.data:
            coupon.enabled=request.data['value']
            coupon.save()
            return Response(CouponSerializer(coupon).data)

class ValidateCouponView(APIView):
    authentication_classes=[TokenAuth]
    permission_classes=[IClient]

    def get(self,request,key):
        coupon=get_object_or_404(Coupon,key=key,enabled=True)
        if not Order.objects.filter(user=request.user.client,coupon=coupon).exists():
            return Response(CouponSerializer(coupon).data)

        return Response('',status=521)


class UserOrdersView(APIView):
    authentication_classes=[TokenAuth]
    permission_classes=[IClient]

    def get(self,request,page):
        historyOrders=Order.objects.filter(Q(user=request.user.client)&Q(Q(status=Order.States.finshed)|Q(status=Order.States.terminate)|Q(status=Order.States.rejected))) if page==1 else []
        currentOrders=(Order.objects.filter(user=request.user.client).exclude(Q(Q(status=Order.States.finshed)|Q(status=Order.States.terminate)|Q(status=Order.States.rejected)))  if page==1 else [] )[25*(page-1):25*page]
        historySeri=OrderReadSerializer(instance=historyOrders,many=True)
        currentSeri=OrderReadSerializer(instance=currentOrders,many=True)
        data={
            'history':historySeri.data,
            "current":currentSeri.data,
        }
        return Response(data)


class CancelOrderView(APIView):
    authentication_classes=[TokenAuth]
    permission_classes=[IClient]


    def put(self,request,pk,*args,**kwargs):
        order=get_object_or_404(Order,id=pk)
        if order.user==request.user.client and order.status ==Order.States.inQueue:
            order.status=Order.States.terminate
            order.save()
            return Response('')
        raise PermissionDenied()


class OrdersProfileView(APIView):

    def get(self,request,pk,page):
        historyOrders=Order.objects.filter(Q(user_id=pk)&Q(Q(status=Order.States.finshed)|Q(status=Order.States.terminate)|Q(status=Order.States.rejected)))
        currentOrders=(Order.objects.filter(user_id=pk).exclude(Q(Q(status=Order.States.finshed)|Q(status=Order.States.terminate)|Q(status=Order.States.rejected)))  if page==1 else [] )[25*(page-1):25*page]
        historySeri=OrderReadSerializer(instance=historyOrders,many=True)
        currentSeri=OrderReadSerializer(instance=currentOrders,many=True)
        data=[*(currentSeri.data),*(historySeri.data)]
        return Response(data)

