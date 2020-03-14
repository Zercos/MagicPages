from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView

from main.forms import ContactForm


class HomeView(TemplateView):
    template_name = 'home.html'


class AboutUsView(TemplateView):
    template_name = 'about.html'


class ContactView(FormView):
    template_name = 'contact_us.html'
    form_class = ContactForm
    success_url = reverse_lazy('main:home')

    def form_valid(self, form):
        form.send_customer_service_email()
        super().form_valid()
