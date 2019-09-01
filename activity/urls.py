from django.urls import path
from . import views

urlpatterns = [

    path("showActivity/", views.showActivity),
    path("createActivity/", views.createActivity),
    path("uploadFile/", views.uploadFile),
    path("pageDisplay/", views.pageDisplay),
    path("editActivity/", views.editActivity),

]