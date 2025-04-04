from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import TripViewSet, LogSheetViewSet

router = DefaultRouter()
router.register(r'trips', TripViewSet)
router.register(r'logsheets', LogSheetViewSet, basename='logsheet')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]