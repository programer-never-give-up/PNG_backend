from django.urls import path
from . import views

urlpatterns=[

    path("showRecent/",views.showRecent),
    path('apply/',views.apply),
    path('collect/',views.collect),
    path('showActivityList/',views.showActivityList),
    path('showModification/',views.showModification),
    path('getQRcode/',views.getQRcode),
    path('add_in_recommendation/',views.add_in_recommendation),
    path('showRecommendation/',views.showRecommendation),
    path('search/',views.search),
]