from django.core.mail import send_mail
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.files.base import ContentFile

from post.models import Post, Comment
from post.serializers import CommentSerializer, PostSerializer


class PostMVS(ModelViewSet):
    serializer_class = PostSerializer
    authentication_classes = [
        JWTAuthentication,
    ]

    def get_queryset(self):
        user = self.request.user
        return Post.objects.filter(author_id=user)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(author=user)


class CommentMVS(ModelViewSet):
    serializer_class = CommentSerializer
    authentication_classes = [
        JWTAuthentication,
    ]

    @property
    def qparams(self) -> dict:
        return self.request.query_params

    def get_queryset(self):
        user = self.request.user
        post_id = self.qparams.get("post") or self.qparams.get("post_id")
        return Comment.objects.filter(post_id=int(post_id), author_id=user)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(author=user)
