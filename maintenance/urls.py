from django.urls import path

from . import views


app_name = "maintenance"

urlpatterns = [
    path("", views.MaintenanceListView.as_view(), name="list"),
    path("pending/", views.MaintenancePendingView.as_view(), name="pending"),
    path("pending/equipment/<int:equipment_id>/", views.MaintenancePendingView.as_view(), name="equipment-pending"),
    path("new/", views.MaintenanceCreateView.as_view(), name="create"),
    path("plans/new/", views.MaintenancePlanCreateView.as_view(), name="plan-create"),
    path("<int:pk>/", views.MaintenanceDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.MaintenanceUpdateView.as_view(), name="update"),
    path(
        "history/<int:equipment_id>/",
        views.MaintenanceHistoryView.as_view(),
        name="history",
    ),
]
