from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView, ListView, DetailView, CreateView, UpdateView, DeleteView

from main import models
from main.forms import ContactForm, UserCreationForm, AuthenticationForm


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
        return super().form_valid(form)


class ProductListView(ListView):
    template_name = 'main/product_list.html'
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


class ProductDetailView(DetailView):
    model = models.Product


class RegistrationView(FormView):
    form_class = UserCreationForm
    template_name = 'signup.html'

    def get_success_url(self):
        redirect = self.request.GET.get('next', '/')
        return redirect

    def form_valid(self, form):
        response = super().form_valid(form)
        form.save()
        email = form.cleaned_data['email']
        password = form.cleaned_data['password1']
        user = authenticate(email=email, password=password)
        login(self.request, user)
        form.send_welcome_email()
        messages.info(self.request, 'You signup successfully')
        return response


class UserLoginView(LoginView):
    template_name = 'login.html'
    form_class = AuthenticationForm


class AddressListView(LoginRequiredMixin, ListView):
    model = models.Address

    def get_queryset(self):
        return models.Address.objects.filter(user=self.request.user)


class AddressCreateView(LoginRequiredMixin, CreateView):
    model = models.Address
    fields = ['name', 'address1', 'address2', 'city', 'zip_code', 'country']
    success_url = reverse_lazy('main:address_list')

    def form_valid(self, form):
        address = form.save(commit=False)
        address.user = self.request.user
        address.save()
        return super().form_valid(form)


class AddressUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Address
    template_name = 'main/address_update.html'
    fields = ['name', 'address1', 'address2', 'city', 'zip_code', 'country']
    success_url = reverse_lazy('main:address_list')

    def get_queryset(self):
        return models.Address.objects.filter(user=self.request.user)


class AddressDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Address
    success_url = reverse_lazy('main:address_list')

    def get_queryset(self):
        return models.Address.objects.filter(user=self.request.user)
