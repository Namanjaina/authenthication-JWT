from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone
from django.urls import reverse
from .models import PasswordReset
import threading


# 🔥 Async email send (IMPORTANT)
def send_email_async(email_message):
    try:
        email_message.send(fail_silently=True)
    except Exception as e:
        print("Email Error:", e)


@login_required
def Home(request):
    return render(request, 'index.html')


def RegisterView(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect('register')

        if len(password) < 5:
            messages.error(request, "Password must be at least 5 characters")
            return redirect('register')

        User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            password=password
        )

        messages.success(request, "Account created successfully. Please login.")
        return redirect('login')

    return render(request, 'register.html')


def LoginView(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials")
            return redirect('login')

    return render(request, 'login.html')


def LogoutView(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('login')


def ForgotPassword(request):
    if request.method == "POST":
        email = request.POST.get('email')

        user = User.objects.filter(email=email).first()

        if user:
            reset_obj = PasswordReset.objects.create(user=user)

            reset_url = reverse('reset-password', kwargs={'reset_id': reset_obj.reset_id})
            full_url = f"{request.scheme}://{request.get_host()}{reset_url}"

            email_body = f"""
Hello {user.username},

Click below link to reset your password:

{full_url}

This link will expire in 10 minutes.
"""

            email_message = EmailMessage(
                'Reset your password',
                email_body,
                settings.EMAIL_HOST_USER,
                [email]
            )

            try:
                # fail_silently=False rakhein taaki error dikhe debug ke waqt
                email_message.send(fail_silently=False)
                return redirect('password-reset-sent', reset_id=reset_obj.reset_id)
            except Exception as e:
                print(f"Email Error: {e}")
                messages.error(request, "there was an error sending the email. Try again later.")
                reset_obj.delete() # Cleanup
                return redirect('forgot-password')
        else:
            messages.error(request, "No account found with this email")
            return redirect('forgot-password')

    return render(request, 'forgot_password.html')


def PasswordResetSent(request, reset_id):
    if PasswordReset.objects.filter(reset_id=reset_id).exists():
        return render(request, 'password_reset_sent.html')
    else:
        messages.error(request, "Invalid reset link")
        return redirect('forgot-password')


def ResetPassword(request, reset_id):
    try:
        reset_obj = PasswordReset.objects.get(reset_id=reset_id)

        # 🔥 Expiration check (10 min)
        if timezone.now() > reset_obj.created_when + timezone.timedelta(minutes=10):
            reset_obj.delete()
            messages.error(request, "Reset link expired")
            return redirect('forgot-password')

        if request.method == "POST":
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if password != confirm_password:
                messages.error(request, "Passwords do not match")
                return redirect('reset-password', reset_id=reset_id)

            if len(password) < 5:
                messages.error(request, "Password must be at least 5 characters")
                return redirect('reset-password', reset_id=reset_id)

            user = reset_obj.user
            user.set_password(password)
            user.save()

            reset_obj.delete()

            messages.success(request, "Password reset successful. Login now.")
            return redirect('login')

    except PasswordReset.DoesNotExist:
        messages.error(request, "Invalid or expired link")
        return redirect('forgot-password')

    return render(request, 'reset_password.html')
