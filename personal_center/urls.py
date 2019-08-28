from django.urls import path
from . import views

urlpatterns=[

    path("showInfo/",views.showInfo),
    path("editInfo/",views.editInfo),
    path('history_attend/',views.history_attend),
    path('history_organize/',views.history_organize),
]