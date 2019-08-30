"""PNG_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from login import views as views_login
from activity import views as views_activity


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views_login.index),
    path('api/index/', views_login.index),
    path('api/login/', views_login.login),

    path('api/check/', views_login.check),  # 确认登录状态
    path('api/register/', views_login.register),
    path('api/logout/', views_login.logout),
    path('api/findPassword/', views_login.findPassword),

    path('api/mail/sendMail/', views_login.sendMail),
    path('api/mail/checkMail/', views_login.checkMail),

    path("api/activity/", include("activity.urls")),
    path('api/personal_center/',include('personal_center.urls')),
    path('api/yw/', include('yw.urls')),

]
