from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import LoginActivity, LoginHistory
from django.utils.timezone import now

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    # Log the login action
    LoginActivity.objects.create(user=user, action='login')

    # Ensure LoginHistory exists or create it if not
    history, created = LoginHistory.objects.get_or_create(user=user)

    # If it's a new history object, initialize the total logins
    if created:
        history.total_logins = 1
    else:
        history.total_logins += 1

    history.last_login = now()  # Update last login time
    history.save()

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    if user.is_authenticated:
        # Log the logout action
        LoginActivity.objects.create(user=user, action='logout')

        # Ensure LoginHistory exists or create it if not
        history, created = LoginHistory.objects.get_or_create(user=user)

        # If it's a new history object, initialize the total logouts
        if created:
            history.total_logouts = 1
        else:
            history.total_logouts += 1

        history.last_logout = now()  # Update last logout time
        history.save()
