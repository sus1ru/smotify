from rest_framework import serializers

from notification.models import Notification, NotificationPreference


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = (
            "id",
            "user",
            "via_app",
            "via_email",
            "via_sms",
        )
        extra_kwargs = {
            "user": {"read_only": True},
        }


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ("id", "user", "is_read", "is_delivered")
        extra_kwargs = {
            "user": {"read_only": True},
        }
