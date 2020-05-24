from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, FormView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django import forms as django_forms
from django.db import models as django_models
import django_filters
from django_filters.views import FilterView

from main import models
from main.forms import ContactForm, UserCreationForm, AuthenticationForm, BasketLineFormSet, AddressSelectionForm


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = models.Product.objects.active()
        pack = products.order_by('name').all()[:6]
        context['products_list'] = [pack[:3], pack[3:]]
        return context


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


def add_to_basket(request):
    product_id = request.GET.get('product_id')
    product = get_object_or_404(models.Product, pk=product_id)
    basket = request.basket
    if not basket:
        user = request.user if request.user.is_authenticated else None
        basket = models.Basket.objects.create(user=user)
        request.session['basket_id'] = basket.id
    basket_line, created = models.BasketLine.objects.get_or_create(basket=basket, product=product)
    if not created:
        basket_line.quantity += 1
        basket_line.save()
    return HttpResponseRedirect(reverse('main:product', args=(product.slug,)))


def manage_basket(request):
    if not request.basket or request.basket.is_empty():
        return render(request, 'basket.html', {'formset': None})
    if request.method == 'POST':
        form = BasketLineFormSet(request.POST, instance=request.basket)
        if form.is_valid():
            form.save()
    else:
        form = BasketLineFormSet(instance=request.basket)
    return render(request, 'basket.html', {'formset': form})


class AddressSelectionView(LoginRequiredMixin, FormView):
    template_name = 'address_select.html'
    form_class = AddressSelectionForm
    success_url = reverse_lazy('main:order_done')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        del self.request.session['basket_id']
        basket = self.request.basket
        basket.create_order(billing_address=form.cleaned_data['billing_address'],
                            shipping_address=form.cleaned_data['shipping_address'])
        return super().form_valid(form)


class DateInput(django_forms.DateInput):
    input_type = 'date'


class OrderFilter(django_filters.FilterSet):
    class Meta:
        model = models.Order

        fields = {
            'user__email': ['icontains'],
            'status': ['exact'],
            'date_updated': ['gt', 'lt'],
            'date_added': ['gt', 'lt'],
        }

        filter_overrides = {
            django_models.DateTimeField: {
                'filter_class': django_filters.DateFilter,
                'extra': lambda f:{
                    'widget': DateInput
                }
            }
        }


class OrderView(UserPassesTestMixin, FilterView):
    filterset_class = OrderFilter
    login_url = reverse_lazy('main:login')

    def test_func(self):
        return self.request.user.is_staff is True
