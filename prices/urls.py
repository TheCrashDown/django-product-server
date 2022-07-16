from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from api import urls as api_urls 


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include(api_urls)),
]