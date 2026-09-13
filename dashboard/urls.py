from django.urls import path

from .views import DashboardView, UniversalSearchView

app_name = "dashboard"

urlpatterns = [
    path("", DashboardView.as_view(), name="index"),
    path("search/", UniversalSearchView.as_view(), name="search"),
]
