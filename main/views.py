from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView, ListView

from main import models
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


class ProductListView(ListView):
    template_name = "main/product_list.html"
    paginate_by = 4

    def get_queryset(self):
        self.tag = None
        tag = self.kwargs['tag']
        if tag != 'all':
            self.tag = get_object_or_404(models.ProductTag, slug=tag)
        if self.tag:
            products = models.Product.objects.active().filter(tags=self.tag)
        else:
            products = models.Product.objects.active()
        return products.order_by('name')
