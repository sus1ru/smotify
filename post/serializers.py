from rest_framework import serializers

from post.models import Post, Comment


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "author", "title", "body", "upvotes", "downvotes")
        extra_kwargs = {
            "author": {"read_only": True},
            "title": {"required": True},
            "body": {"required": True},
        }


class CommentSerializer(serializers.ModelSerializer):
    parent_id = serializers.IntegerField()

    class Meta:
        model = Comment
        fields = (
            "id",
            "author",
            "post",
            "parent_id",
            "title",
            "body",
            "upvotes",
            "downvotes",
        )
        extra_kwargs = {
            "author": {"read_only": True},
            "post": {"required": True},
            "title": {"required": True},
            "body": {"required": True},
        }
