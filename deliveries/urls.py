from django.urls import path

from . import views


app_name = "deliveries"

urlpatterns = [
    path("", views.DeliveryListView.as_view(), name="list"),
    path("new/", views.DeliveryCreateView.as_view(), name="create"),
    path("<int:pk>/", views.DeliveryDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.DeliveryUpdateView.as_view(), name="update"),
]
