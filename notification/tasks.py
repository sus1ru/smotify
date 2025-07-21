from dateutil.relativedelta import relativedelta
from celery import shared_task

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail

from notification.models import Notification


def send_sms():
    pass


@shared_task(time_limit=600, retries=3, soft_time_limit=600, queue="notify")
def post_process_notification(notification_id: int = None):
    if notification_id:
        notifications = Notification.objects.select_related(
            "user", "user__preference"
        ).filter(id=notification_id, is_delivered=False)

    for notification in notifications:
        preference = notification.user.preference
        mail_to = str(notification.user.email)
        template = "notification_template.html"
        email_data = {
            "is_read": notification.is_read,
            "date_created": notification.date_created,
            "message": notification.formatted_body,
        }
        html_message = render_to_string(
            template,
            email_data,
        )
        email_message = strip_tags(html_message)
        if preference.via_email:
            try:
                email_res = send_mail(
                    subject=notification.formatted_title,
                    message=email_message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[
                        mail_to,
                    ],
                    html_message=html_message,
                    fail_silently=False,
                )
                email_delivery = True
            except Exception as e:
                email_delivery = False

        if preference.via_sms:
            try:
                sms_res = send_sms()
                sms_delivery = True
            except Exception as e:
                sms_delivery = False

        notification.is_delivered = email_delivery and sms_delivery
        notification.save()
