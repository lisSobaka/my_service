from django.urls import path
from .views import *


    # CLIENTS
urlpatterns = [    
    path('', ClientsView.as_view(), name='clients'),
    path('<int:client_id>/edit', EditClient.as_view(), name='edit_client'),
    ]
