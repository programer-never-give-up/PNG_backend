from django.urls import path
from . import views

urlpatterns=[

    path("showRecent/",views.showRecent),
    path('apply/',views.apply),

]