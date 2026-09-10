from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import DeliveryForm
from .models import Delivery
from organizations.tenant import get_user_organization


class DeliveryListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = "deliveries.view_delivery"
    model = Delivery
    template_name = "deliveries/delivery_list.html"
    context_object_name = "deliveries"
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().filter(organization=get_user_organization(self.request.user)).select_related("equipment", "delivered_by")


class DeliveryDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = "deliveries.view_delivery"
    model = Delivery
    template_name = "deliveries/delivery_detail.html"
    context_object_name = "delivery"

    def get_queryset(self):
        return super().get_queryset().filter(organization=get_user_organization(self.request.user))


class DeliveryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "deliveries.add_delivery"
    model = Delivery
    form_class = DeliveryForm
    template_name = "deliveries/delivery_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organization"] = get_user_organization(self.request.user)
        return kwargs

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.organization = get_user_organization(self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("deliveries:list")


class DeliveryUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "deliveries.change_delivery"
    model = Delivery
    form_class = DeliveryForm
    template_name = "deliveries/delivery_form.html"

    def get_queryset(self):
        return super().get_queryset().filter(organization=get_user_organization(self.request.user))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organization"] = get_user_organization(self.request.user)
        return kwargs

    def get_success_url(self):
        return reverse("deliveries:detail", args=[self.object.pk])
