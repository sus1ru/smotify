from django.apps import apps
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import CharField
from django.db.models.functions import Lower
from django.contrib.contenttypes.models import ContentType

from treebeard.mp_tree import MP_Node

from notification.models import Notification, SubscriptionAlert
from notification.tasks import post_process_notification


class NotificationSetting:
    ACTION_TYPES = ["post", "comment"]
    NOTIFICATION_SETTINGS = {
        "user": {
            "model": "user.User",
            "ctype": ContentType.objects.get(app_label="user", model="User").id,
        },
        "post": {
            "model": "post.Post",
            "ctype": ContentType.objects.get(app_label="post", model="Post").id,
        },
        "comment": {
            "model": "post.Comment",
            "ctype": ContentType.objects.get(app_label="post", model="Comment").id,
        },
    }

    @property
    def ctypes(self):
        return [v.get("ctype") for _, v in self.NOTIFICATION_SETTINGS.items()]


class NotificationHandler(NotificationSetting):
    def __init__(self, action_type: str, object_id: int):
        self.action_type = action_type
        self.object_id = object_id
        self.model = apps.get_model(action_type)

        self.action = self.model.objects.select_related("author").get(id=object_id)
        self.triggerer = getattr(self.action, "author")
        self.subscribed_objects = [self.triggerer.id]
        self.callback_handlers = {
            "post": self.post_handler,
            "comment": self.comment_handler,
        }
        self.callback_handlers.get(self.action_type)()

    @property
    def action_type(self):
        return getattr(self, "_action_type", None)

    @action_type.setter
    def action_type(self, val):
        val = val.lower()
        if val not in self.ACTION_TYPES:
            raise ValueError("InitError: Invalid model alias")

        setattr(self, "_action_type", val)

    def get_notification_content(self, action_type):
        if action_type == "post":
            title = {"main": "New Post"}
            body = {"main": "<triggerer> posted a new thread."}

        elif action_type == "comment":
            title = {"main": "New Comment"}
            body = {"main": "<triggerer> replied in the thread."}

        else:
            return None, None

        body["dynamic"] = {
            "triggerer": {
                "model": "user.User",
                "pk": self.triggerer.id,
                "field": "username",
            }
        }
        return title, body

    def post_handler(self):
        pass

    def comment_handler(self):
        if hasattr(self.action, "post_id"):
            self.subscribed_objects.append(self.action.post_id)

        if issubclass(self.action, MP_Node):
            parent = self.action.get_parent()
            if parent:
                self.subscribed_objects.append(parent.id)

    def process_user_subscriptions(self):
        return (
            SubscriptionAlert.objects.filter(
                content_type_in=self.ctypes,
                object_id__in=self.subscribed_objects,
            )
            .values_list("subscriber_id", flat=True)
            .distinct()
        )

    def create_notification(self):
        title, body = self.get_notification_content(self.action_type)

        for pk in self.process_user_subscriptions():
            notification = Notification(user_id=pk, title=title, body=body)
            notification.save()
            post_process_notification.delay(notification_id=notification.id)
