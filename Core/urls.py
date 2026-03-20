from django.urls import path
from . import views
from django.shortcuts import redirect # Redirect ke liye

urlpatterns = [
    # 1. Homepage
    path('', views.Home, name='home'),

    # 2. Authentication (Traditional Views)
    path('register/', views.RegisterView, name='register'),
    path('login/', views.LoginView, name='login'),
    path('logout/', views.LogoutView, name='logout'),

    # 3. Password Management
    path('forgot-password/', views.ForgotPassword, name='forgot-password'),
    path('password-reset-sent/<str:reset_id>/', views.PasswordResetSent, name='password-reset-sent'),
    path('reset-password/<str:reset_id>/', views.ResetPassword, name='reset-password'),

    # 4. FIX: Redirect /accounts/login/ to /login/ 
    # Isse wo 404 error hamesha ke liye khatam ho jayega
    path('accounts/login/', lambda request: redirect('login')),
]