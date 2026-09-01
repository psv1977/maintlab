from django.urls import path

from . import views


app_name = "equipment"

urlpatterns = [
    path("", views.EquipmentListView.as_view(), name="list"),
    path("new/", views.equipment_create, name="create"),
    path("<int:pk>/", views.EquipmentDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.equipment_update, name="update"),
    path("<int:pk>/retire/", views.equipment_retire, name="retire"),
]
