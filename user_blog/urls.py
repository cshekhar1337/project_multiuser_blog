"""blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name = "Home"),
    url(r'^logout/$', views.logout, name = "logout"),
    url(r'^register/$', views.register, name = "register"),
    url(r'^blogview/$', views.login, name = "blogview"),
    url(r'^addpost/$', views.addpost, name = "addpost"),
    url(r'^blog/$', views.blog_view, name = "blog_view"),
    url(r'^likepost/(?P<pid>[0-9]+)/$', views.likepost, name = "likepost"),
    url(r'^editpost/(?P<pid>[0-9]+)/$', views.editpost, name = "editpost"),


]
