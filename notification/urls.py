from django.urls import include, path
from rest_framework.routers import DefaultRouter

from notification.viewsets import NotificationPreferenceVS, NotificationMVS, subscribe


router = DefaultRouter()

router.register(r"", NotificationMVS, basename="notification")

urlpatterns = [
    path("", include(router.urls)),
    path("subscribe/", subscribe, name="subscribe"),
    path(
        "preference/<int:pk>/",
        NotificationPreferenceVS.as_view(),
        name="notification_preference",
    ),
]
