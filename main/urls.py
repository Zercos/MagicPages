from django.urls import path

from main import views

app_name = 'main'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about-us/', views.AboutUsView.as_view(), name='about_us'),
    path('contact-us/', views.ContactView.as_view(), name='contact_us'),
    path('products/<slug:tag>/', views.ProductListView.as_view(), name='products', ),
]
