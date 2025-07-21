from django.db.models.signals import post_save
from django.dispatch import receiver

from notification.models import SubscriptionAlert
from post.models import Comment, Post


@receiver(post_save, sender=Post)
@receiver(post_save, sender=Comment)
def subscribe_users_to_topics(sender, instance, created, raw, **kwargs):
    if created:
        author = getattr(instance, "author", None)
        if author:
            sub = SubscriptionAlert(subscriber=author, subscribed_to=instance)
            sub.save()
