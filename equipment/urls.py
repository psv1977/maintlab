from django.urls import path

from . import views


app_name = "equipment"

urlpatterns = [
    path("", views.EquipmentListView.as_view(), name="list"),
    path("new/", views.EquipmentCreateView.as_view(), name="create"),
    path("locations/new/", views.LocationCreateView.as_view(), name="location-create"),
    path("<int:equipment_id>/identifiers/new/", views.EquipmentIdentifierCreateView.as_view(), name="identifier-create"),
    path("<int:equipment_id>/readings/new/", views.MeterReadingCreateView.as_view(), name="reading-create"),
    path("import/", views.EquipmentImportView.as_view(), name="import"),
    path("<int:pk>/", views.EquipmentDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.EquipmentUpdateView.as_view(), name="update"),
    path("<int:pk>/retire/", views.EquipmentRetireView.as_view(), name="retire"),
]
