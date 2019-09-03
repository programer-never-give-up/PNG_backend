from django.urls import path
from . import views

urlpatterns = [

    path("showActivity/", views.showActivity),
    path("createActivity/", views.createActivity),
    path("uploadFile/", views.uploadFile),
    path("pageDisplay/", views.pageDisplay),
    path("editActivity/", views.editActivity),
    path("deleteActivity/", views.deleteActivity),
    path("publishActivity/", views.publishActivity),
    path("adminAgreeModify/", views.adminAgreeEdit),
    path("adminRefuseModify/", views.adminRefuseEdit),
    path("adminAgreeDelete/", views.adminAgreeDelete),
    path("adminRefuseDelete/", views.adminRefuseDelete),
    path("adminAgreePublish/", views.adminAgreePublish),
    path("adminRefusePublish/", views.adminRefusePublish),

]
