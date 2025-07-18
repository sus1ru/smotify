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
    parent_id = serializers.IntegerField(
        required=False, allow_null=True, write_only=True
    )

    class Meta:
        model = Comment
        fields = (
            "id",
            "author",
            "post",
            "parent_id",
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

    def create(self, validated_data):
        parent_id = validated_data.pop("parent_id", None)

        if parent_id is not None:
            try:
                parent = Comment.objects.get(id=parent_id)
                return parent.add_child(**validated_data)
            except (Comment.DoesNotExist, ValueError) as e:
                raise serializers.ValidationError("Error: Parent post doesnot exist!")
        else:
            return Comment.add_root(**validated_data)
