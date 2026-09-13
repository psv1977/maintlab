from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView

from .forms import CustomerForm
from .models import Customer
from .tenant import get_user_organization


class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = "organizations/customer_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organization"] = get_user_organization(self.request.user)
        return kwargs

    def form_valid(self, form):
        form.instance.organization = get_user_organization(self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("equipment:create")
