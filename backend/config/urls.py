from django.contrib import admin
from django.urls import path

from followup.views import FollowUpContactView, FollowUpListView


urlpatterns = [
    path("admin/", 
         admin.site.urls
    ),
    path("api/follow-up", 
         FollowUpListView.as_view(), 
         name="follow-up"
    ),
    path(
        "api/follow-up/<int:pk>/contacted",
        FollowUpContactView.as_view(),
        name="follow-up-contacted",
    )
]