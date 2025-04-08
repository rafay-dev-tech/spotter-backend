from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TripViewSet, LogSheetViewSet

router = DefaultRouter()
router.register(r'trips', TripViewSet, basename='trip')
router.register(r'logsheets', LogSheetViewSet, basename='logsheet')

urlpatterns = [
    path('', include(router.urls)),
] 