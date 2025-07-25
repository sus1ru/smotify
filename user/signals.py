from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode

from user.utils import account_activation_token


@receiver(post_save, sender=get_user_model())
def send_activation_email(sender, instance, created, raw, **kwargs):
    if created:
        current_site = settings.BACKEND_URL
        email_subject = "Activate your smotify mail"
        template = "account_activation_email.html"

        email_data = {
            "name": instance.username,
            "user": instance,
            "domain": current_site,
            "uid": urlsafe_base64_encode(force_bytes(instance.pk)),
            "token": account_activation_token.make_token(instance),
        }
        mail_to = str(instance.email)
        html_message = render_to_string(
            template,
            email_data,
        )
        email_message = strip_tags(html_message)

        email_res = send_mail(
            email_subject,
            email_message,
            settings.EMAIL_HOST_USER,
            [mail_to,],
            html_message=html_message,
            fail_silently=False,
        )
        email_response = (
            ", Confirm your email address.".format(mail_to)
            if email_res
            else "Email verification could not be done."
        )
