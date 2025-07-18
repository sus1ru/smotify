from django.db import models
from django.conf import settings

from treebeard.mp_tree import MP_Node


class BaseModel(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)ss",
        blank=True,
        null=True,
    )
    body = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False, blank=True, null=True)
    upvotes = models.PositiveIntegerField(default=0, blank=True, null=True)
    downvotes = models.PositiveIntegerField(default=0, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True


class Post(BaseModel):
    title = models.CharField(max_length=256, null=True, blank=True)


class Comment(BaseModel, MP_Node):
    post = models.ForeignKey(
        "Post", on_delete=models.CASCADE, related_name="comments", blank=True, null=True
    )

    node_order_by = ["-date_created"]
