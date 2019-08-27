from django.urls import path
from . import views

urlpatterns=[

    path("showInfo/",views.showInfo),
    path("editInfo/",views.editInfo),

]