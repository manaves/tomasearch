"""
URL configuration for tomasearch project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from myapp.views import *
import debug_toolbar

urlpatterns = [
    path('', home_page, name='home'),
    path('how_it_works/', how_it_works_page, name='how_it_works'),
    path('information/', information_page, name='information'),
    path('search/', search, name='search'),
    path('search_gene/', search_gene, name='search_gene'),
    path('search_go_identifier/', search_go_identifier, name='search_go_identifier'),
    path('search_go_term/', search_go_term, name='search_go_term'),
    path('search_subontology/', search_subontology, name='search_subontology'),
    path('download_csv/', download_csv, name='download_csv'),
    path('images/', images_page, name='images'),
    path('admin/', admin.site.urls),
    path('__debug__/', include(debug_toolbar.urls)),
]
