from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from soc import views
router = DefaultRouter()
router.register('threats', views.ThreatViewSet, basename='threat')
router.register('incidents', views.IncidentViewSet, basename='incident')
router.register('alerts', views.AlertViewSet, basename='alert')
router.register('audit', views.AuditViewSet, basename='audit')
urlpatterns = [path('api/health/',views.health), path('api/auth/login/',TokenObtainPairView.as_view()), path('api/auth/refresh/',TokenRefreshView.as_view()), path('api/auth/register/',views.RegisterView.as_view()), path('api/auth/profile/',views.profile), path('api/auth/logout/',views.logout), path('api/analytics/dashboard/',views.dashboard), path('api/settings/',views.settings_view), path('api/users/',views.UsersView.as_view()), path('api/',include(router.urls))]
