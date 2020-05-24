from django.urls import path
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView

from main import views

app_name = 'main'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about-us/', views.AboutUsView.as_view(), name='about_us'),
    path('contact-us/', views.ContactView.as_view(), name='contact_us'),
    path('products/<slug:tag>/', views.ProductListView.as_view(), name='products'),
    path('product/<slug:slug>', views.ProductDetailView.as_view(), name='product'),
    path('signup/', views.RegistrationView.as_view(), name='signup'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('address/', views.AddressListView.as_view(), name='address_list'),
    path('address/create/', views.AddressCreateView.as_view(), name='address_create'),
    path('address/<int:pk>/', views.AddressUpdateView.as_view(), name='address_update'),
    path('address/<int:pk>/delete/', views.AddressDeleteView.as_view(), name='address_delete'),
    path('add-to-basket/', views.add_to_basket, name='add_to_basket'),
    path('manage-basket/', views.manage_basket, name='manage_basket'),
    path('select-address/', views.AddressSelectionView.as_view(), name='address_select'),
    path('order-done/', TemplateView.as_view(template_name='order_done.html'), name='order_done'),
    path("order-dashboard/", views.OrderView.as_view(), name='order_dashboard'),
]
