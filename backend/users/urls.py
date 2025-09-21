from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('signout/', views.signout_view, name='signout'),
    path('userinfo/', views.userinfo_view, name='userinfo'),
]