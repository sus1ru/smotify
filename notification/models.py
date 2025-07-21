from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.conf import settings


class BaseModel(models.Model):
    date_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True


class SubscriptionAlert(BaseModel):
    subscriber = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_subscriptions",
        blank=True,
        null=True,
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    subscribed_to = GenericForeignKey("content_type", "object_id")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["content_type", "object_id", "subscriber"],
                name="unique_user_subs",
            )
        ]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]


class NotificationPreference(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="preference",
        blank=True,
        null=True,
    )

    via_app = models.BooleanField(default=True, blank=True, null=True)
    via_email = models.BooleanField(default=True, blank=True, null=True)
    via_sms = models.BooleanField(default=True, blank=True, null=True)


class Notification(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        blank=True,
        null=True,
    )
    is_read = models.BooleanField(default=False, blank=True, null=True)
    is_delivered = models.BooleanField(default=False, blank=True, null=True)

    title = models.JSONField(blank=True, null=True)
    body = models.JSONField(blank=True, null=True)

    @property
    def formatted_title(self):
        return self.title.get("main")

    @property
    def formatted_body(self):
        body_template = self.body.get("main")
        for key, val in self.body.items():
            model = apps.get_model(val.get("model"))
            pk = val.get("pk")
            try:
                data = getattr(model.objects.get(id=pk), val.get("field"))
            except model.DoesNotExist as e:
                continue
            body_template.replace(key, data)
        return body_template
