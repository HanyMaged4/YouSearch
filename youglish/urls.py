from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from api.api import api as ninja_api

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('admin/', admin.site.urls),
    path('api/', ninja_api.urls),
]
