from django.urls import path
from .views import *


urlpatterns = [
    # ORDERS
    path('', OrdersView.as_view(), name='orders'),
    path('new_order/', CreateOrder.as_view(), name='create_order'),
    path('order/<int:order_id>', OrderDetail.as_view(), name='order'),
    path('order/<int:order_id>/edit/', EditOrder.as_view(), name='edit_order'),
    path('order/<int:order_id>/delete/', DeleteOrder.as_view(), name='delete_order'),
    # path('order/<int:order_id>/close_order/', CloseOrder.as_view(), name='close_order'),
]

