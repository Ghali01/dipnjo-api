from this import d
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from firebase_admin import messaging

from foods.models import Food
from util.noitfication import NotificationTypes
from .serializers import *
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.db.models import F,Count
from util.authentection import TokenAuth
from util.permissions import IClient
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin,ListModelMixin
class ClientUserView(APIView):


    def post(self,request):
        if 'user' in request.data:
            serailizerd=ClientUserSerializer(data=request.data)
            if serailizerd.is_valid(raise_exception=True):
                serailizerd.save()
            return Response(serailizerd.data,status=201)
        else:
            raise ValidationError('user is required')

class SetFCMTokenView(APIView):
    authentication_classes=[TokenAuth]
    permission_classes=[IClient]

    def put(self,request):
        if 'token' in request.data:
            user=request.user
            user.fcmToken=request.data['token']
            user.save()
            if hasattr(user,'client'):
                user.client.subcicribeTopics()
            return Response('done')
        raise ValidationError('token is required')


@api_view(['GET'])
def checkPhone(request):
    resault ={}
    if 'phone' in request.GET:
        resault['exists']=ClientUser.objects.filter(phone=request.GET['phone']).exists()
        return Response(data=resault)
    else:
        raise ValidationError('phone required')

@api_view(['PUT'])
def chargePoints(request):
    if 'points' in request.data and 'token' in request.data:
        user=get_object_or_404(ClientUser,user__token=request.data['token'])
        user.points=F('points')+request.data['points']
        user.save()
        user.refresh_from_db()
        return Response({"points":user.points})
    raise ValidationError()

class FavoriteFood(APIView):
    authentication_classes=[TokenAuth]
    permission_classes=[IClient]

    def put(self,request,pk):
        food=get_object_or_404(Food,id=pk)
        request.user.client.favorites.add(food)
        return Response()
    def delete(self,request,pk):
        food=get_object_or_404(Food,id=pk)
        request.user.client.favorites.remove(food)
        return Response()

class LocationView(GenericAPIView,CreateModelMixin,ListModelMixin):

    serializer_class=LocationSerializer
    authentication_classes=[TokenAuth]
    permission_classes=[IClient]

    def get_queryset(self):
        return self.request.user.client.locations.all()

    def post(self,request):
        request.data['user']=request.user.client.id
        return self.create(request)

    def get(self,request):
        return self.list(request)

class ProfileView(APIView):
    authentication_classes=[TokenAuth]
    

    def get(self,request):
        serializered=ClientUserSerializer(request.user.client)
        return Response(serializered.data)

    def put(self,request):
        if 'phone' in request.data:
            request.user.client.phone=request.data['phone']
            request.user.client.save()
            return Response()
        raise ValidationError()


class LoginView(APIView):
    authentication_classes=[TokenAuth]
    permission_classes=[IClient]

    def get(self,request):
        data={'phone':request.user.client.phone}
        if request.user.client.locations.count()>0:
           data['location']= LocationSerializer(request.user.client.locations.first()).data
        else:
            data['location']=None
        return Response(data)


class UserShareDataView(APIView):
    authentication_classes=[TokenAuth]
    permission_classes=[IClient]

    def get(self,request):
        data={
            'usersSharedCount':request.user.client.usersSharedCount,
            'shareCodeValidated':request.user.client.shareCodeValidated,
            'code':request.user.client.id,
        }
        return Response(data=data)


class ScanShareCodeView(APIView):
    authentication_classes=[TokenAuth]
    permission_classes=[IClient]


    def put(self,request):
        if 'code' in request.data:
            userOfCode=get_object_or_404(ClientUser,id=request.data['code'])
            user=request.user.client
            if not user.shareCodeValidated and not user==userOfCode:
                user.shareCodeValidated=True
                user.save()
                userOfCode.points=F('points')+200
                userOfCode.usersSharedCount=F('usersSharedCount')+1
                userOfCode.save()
                return Response()
        raise ValidationError()


class RateView(APIView):
    authentication_classes=[TokenAuth]
    permission_classes=[IClient]

    def put(self,request):
        if 'value' in request.data:
            user=request.user.client
            user.rate=request.data['value']
            user.save()
            return Response()
        raise ValidationError()

    def get(self,request):
        rateData=ClientUser.objects.exclude(rate=None).values('rate').annotate(count=Count('rate'))
        myRate=request.user.client.rate
        data={
            "rateData":rateData,
            "myRate":myRate
        }
        return Response(data)

@api_view(['GET'])
def test(request):
    msg=messaging.Message(
    notification=messaging.Notification(
        title='New Order',
        body='there is new order'
    ),
    data={
        'type':str(NotificationTypes.newOrder),
        'id':str(18)
    },
    topic='admin'

    )
    r=messaging.send(msg)
        
    return Response()

@api_view(['POST'])
def sendNotification(request):
    if 'targetType' in request.data and 'title' in request.data and 'body' in request.data: 
        targetType=request.data['targetType']
        notification=messaging.Notification(title=request.data['title'],body=request.data['body'])
        data={
            "type":str(NotificationTypes.notification)
        }
        if targetType=='all':
            msg=messaging.Message(
                notification=notification,
                topic='user',
                data=data
            )
            r=messaging.send(msg)
        elif targetType=='age' and 'range' in request.data :
            rng=request.data['range'].split('-')
            messages=[]
            for y in range(int(rng[0]),int(rng[1])):
                msg=messaging.Message(
                    notification=notification,
                    topic=f'b-{y}',
                    data=data
                )
                messages.append(msg)
            r=messaging.send_all(messages)
        elif targetType=='user' and 'id' in request.data :
            token=get_object_or_404(ClientUser,id=request.data['id']).user.fcmToken
            msg=messaging.Message(
                notification=notification,
                token=token,
                data=data
            )
            r=messaging.send(msg)
        else: 
            raise ValidationError()

        return Response()

    raise ValidationError()

class UsersView(GenericAPIView,ListModelMixin):
    serializer_class=UserListSerializer
    queryset=ClientUser.objects.all()


    def filter_queryset(self, queryset):
        if 'name' in self.request.GET and not self.request.GET['name']=='':
            queryset=queryset.filter(user__name__startswith=self.request.GET['name'])
        return queryset[20*(self.kwargs['page']-1):20*(self.kwargs['page'])]


    def get(self,request,*args,**kwargs):
        return self.list(request)


