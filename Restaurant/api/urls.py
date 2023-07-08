from django.urls import path
from .views import *

urlpatterns = [
    path('product', ProductView.as_view()),
    path('products', AllProductsList_1.as_view()),
    path('', WebhookView.as_view()),
    path('orders', Order.as_view()),
    path('orderitem', OrderItems.as_view()),
    path('order_list', AllOrders.as_view()),
    path('tracking', TrackOrders.as_view()),
    path('home', Home.as_view())

]
