from django.contrib import admin
from django.urls import path, include
from views import (CategoryListCreateAPIView, CategoryRetrieveUpdateDestroyAPIView,
                   TransactionListCreateAPIView, TransactionRetrieveUpdateDestroyAPIView)
app_name = 'api'

urlpatterns = [
    path('categories/',CategoryListCreateAPIView.as_view(),name='category-list-create'),

    path('categories/<int:pk>/',CategoryRetrieveUpdateDestroyAPIView.as_view(),name='category-detail'),

    path('transactions/',TransactionListCreateAPIView.as_view(),name='transaction-list-create'),

    path('transactions/<int:pk>/',TransactionRetrieveUpdateDestroyAPIView.as_view(),name='transaction-detail'),
]