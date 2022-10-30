from rest_framework.serializers import ModelSerializer
from rest_framework.fields import CharField
from .models import ClientUser, Location,User
class UserSerializer(ModelSerializer):
    class Meta:
        model=User
        fields=['token','name','fcmToken']
class ClientUserSerializer(ModelSerializer):
    user=UserSerializer(required=False)
    class Meta:
        model=ClientUser
        exclude=['favorites']

    def create(self, validated_data):
        user=UserSerializer(data=validated_data['user'])
        user.is_valid()
        user.save()
        
        cu= ClientUser.objects.create(phone= validated_data['phone']if 'phone' in validated_data else None,
                                        gender=validated_data['gender'],
                                        email=validated_data['email'] if 'email' in validated_data else None,
                                        birth=validated_data['birth'],
                                        user=user.instance)
        cu.subcicribeTopics()
        return cu


class LocationSerializer(ModelSerializer):
    class Meta:
        model=Location
        fields='__all__'

class UserListSerializer(ModelSerializer):
    name=CharField(source='user.name')
    class Meta: 
        model=ClientUser
        fields=['id','name','email','phone']
        