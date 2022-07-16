from django.contrib import admin
from django.urls import path, include
from .views import ShopUnitGetAllView, ShopUnitCreateView, ShopUnitGetItemView, \
    ShopUnitStatisticsGetView, ShopUnitSalesView, ShopUnitDeleteView

urlpatterns = [
    path('all', ShopUnitGetAllView.as_view()),
    path('imports', ShopUnitCreateView.as_view()),
    path('nodes/<str:pk>', ShopUnitGetItemView.as_view()),
    path('node/<str:pk>/statistic', ShopUnitStatisticsGetView.as_view()),
    path('sales', ShopUnitSalesView.as_view()),
    path('delete/<str:pk>', ShopUnitDeleteView.as_view())
]
