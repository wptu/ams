from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Test endpoints
    path('test/ping/', views.test_ping, name='test_ping'),
    path('test/json/', views.test_json, name='test_json'),
]
