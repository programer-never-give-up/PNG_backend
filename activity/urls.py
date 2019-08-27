from django.urls import path
from . import views

urlpatterns=[

    path("showActivity/",views.showActivity),
    path("createActivity/",views.createActivity),

]