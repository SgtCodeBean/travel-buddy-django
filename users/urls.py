from django.urls import path
from . import views
app_name = 'users'
urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/<str:username>', views.profile, name='profile'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('manage_users/', views.manage_users, name='manage_users'),
    path('profile/<str:username>/edit_profile', views.edit_profile, name='edit_profile'),
]