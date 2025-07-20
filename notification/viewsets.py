from django.apps import apps
from django.db.models import Q
from django.db import IntegrityError
from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.decorators import api_view, action
from rest_framework.views import Response
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from notification.models import (
    Notification,
    NotificationPreference,
    SubscriptionAlert,
)
from notification.serializers import (
    NotificationPreferenceSerializer,
    NotificationSerializer,
)


@api_view(["POST"])
def subscribe(request):
    user = request.user
    object_id = request.data.get("id")
    subscribe_type = request.data.get("subscribe_type")

    subscribe_types = {
        "user": "auth.User",
        "post": "post.Post",
        "comment": "post.Comment",
    }

    if subscribe_type not in subscribe_types:
        return Response(
            {"Error": "Invalid subscription type"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        model_alias = subscribe_types.get(subscribe_type)
        model = apps.get_model(model_alias)
        subscribed_to = model.objects.get(id=object_id)
        subscription = SubscriptionAlert.objects.create(
            subscriber=user, subscribed_to=subscribed_to
        )

    except (model.DoesNotExist, IntegrityError) as e:
        return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {"Error": "Something went wrong!"}, status=status.HTTP_400_BAD_REQUEST
        )

    return Response(
        {"Success": "User has subscribed successfully"}, status=status.HTTP_201_CREATED
    )


class NotificationPreferenceVS(RetrieveUpdateAPIView):
    serializer_class = NotificationPreferenceSerializer
    authentication_classes = [
        JWTAuthentication,
    ]

    def get_queryset(self):
        return NotificationPreference.objects.filter(user=self.request.user)


class NotificationMVS(ModelViewSet):
    serializer_class = NotificationSerializer
    authentication_classes = [
        JWTAuthentication,
    ]

    @property
    def qparams(self) -> dict:
        return self.request.query_params

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(author=user)

    @action(detail=False, methods=["get"])
    def history(self, request):
        user = request.user
        result = Notification.objects.filter(user=user).values(
            "id", "title", "body", "is_read"
        )
        return Response(
            result,
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def unread(self, request):
        user = request.user
        result = Notification.objects.filter(user=user, is_read=False).values(
            "id", "title", "body", "is_read"
        )
        return Response(
            result,
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"])
    def read(self, request):
        user = request.user
        read_type = self.qparams.get("type")
        filter_dict = Q(user=user, is_read=False)

        if read_type != "all":
            pk = request.data.get("object_id")
            filter_dict &= Q(id=pk)

        Notification.objects.filter(filter_dict).update(is_read=True)
        return Response(
            {"message": f"Notifications marked as read."},
            status=status.HTTP_200_OK,
        )
