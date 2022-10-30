from django.urls import path
from .views import *

urlpatterns=[
    path('add-cart-item',CartItemView.as_view(),name='add-cart-item'),
    path('del-cart-item/<int:pk>',CartItemView.as_view(),name='del-cart-item'),
    path('user-cart',UserCartView.as_view(),name='user-cart'),
    path('send-order',SendOrederView.as_view(),name='send-order'),
    path('set-order-status',setOrderStatus,name='set-order-status'),
    path('orders/<int:page>',OrdersView.as_view(),name='orders'),
    path('order/<int:pk>',OrderView.as_view(),name='order'),
    path('coupons/<int:page>',CouponView.as_view(),name='coupons'),
    path('coupon',CouponView.as_view(),name='coupons'),
    path('coupon/<int:pk>',CouponView.as_view(),name='coupons'),
    path('validate-coupon/<key>',ValidateCouponView.as_view(),name='validate-coupon'),
    path('user-orders/<int:page>',UserOrdersView.as_view(),name='user-orders'),
    path('orders-profile/<int:pk>/<int:page>',OrdersProfileView.as_view(),name='orders-profile'),
    path('cancel-order/<int:pk>',CancelOrderView.as_view(),name='cancel-order'),

]
