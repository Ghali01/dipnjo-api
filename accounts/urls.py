from django.urls import path
from .views import *

urlpatterns=[
    path('create',ClientUserView.as_view(),name='create'),
    path('check-phone',checkPhone,name='check-phone'), 
    path('charge',chargePoints,name='charge-points'),
    path('set-fcm-token',SetFCMTokenView.as_view(),name='set-fcm-token'),
    path('favorite-food/<int:pk>',FavoriteFood.as_view(),name='favorite-food'),
    path('location',LocationView.as_view(),name='location'),
    path('profile',ProfileView.as_view(),name='profile'),
    path('login',LoginView.as_view(),name='login'),
    path('share-data',UserShareDataView.as_view(),name='share-data'),
    path('scan-code',ScanShareCodeView.as_view(),name='scan-code'),
    path('rate',RateView.as_view(),name='rate'),
    path('send-noti',sendNotification,name='send-noti'),
    path('users/<int:page>',UsersView.as_view(),name='users'),
    path('test',test,name='test'),

]