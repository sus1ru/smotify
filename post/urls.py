from django.urls import include, path
from rest_framework.routers import DefaultRouter

from post.viewsets import CommentMVS, PostMVS


router = DefaultRouter()

router.register(r"post", PostMVS, basename="post")
router.register(r"comment", CommentMVS, basename="comment")

urlpatterns = [
    path("", include(router.urls)),
]