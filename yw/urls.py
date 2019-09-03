from django.urls import path
from . import views

urlpatterns=[

    path("showRecent/",views.showRecent),
    path('apply/',views.apply),
    path('collect/',views.collect),
    path('showActivityList/',views.showActivityList),
    path('showModification/',views.showModification),
]