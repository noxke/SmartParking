"""
URL configuration for SmartParking project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from api_device.api_views import api_handler as device_handler
from api_manage.api_views import api_handler as manage_handler
from api_app.api_views import api_handler as app_handler
from .api_views import api_handler

urlpatterns = [
    path('api/device/<path:path>', device_handler, name='device_handler'),
    path('api/manage/<path:path>', manage_handler, name='manage_handler'),
    path('api/app/<path:path>', app_handler, name='app_handler'),
    path('api<path:path>', api_handler, name='api_handler'),
]
