from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication endpoints
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('signout/', views.signout_view, name='signout'),
    path('userinfo/', views.userinfo_view, name='userinfo'),
    
    # JWT specific endpoints
    path('refresh/', views.refresh_token_view, name='refresh_token'),
    path('verify/', views.verify_token_view, name='verify_token'),
]