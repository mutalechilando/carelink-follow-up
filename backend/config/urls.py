from django.contrib import admin
from django.urls import path

from followup.views import FollowUpListView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/follow-up", FollowUpListView.as_view(), name="follow-up"),
]