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
    path("adminAgreeEdit/", views.adminAgreeEdit),
    path("admin/refuseEdit/", views.adminRefuseEdit),
    path("adminAgreeDelete/", views.adminAgreeDelete),
    path("admin/refuseDelete/", views.adminRefuseDelete),
    path("adminAgreePublish/", views.adminAgreePublish),
    path("admin/refusePublish/", views.adminRefusePublish),

]
