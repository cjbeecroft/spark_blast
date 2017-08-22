from django.conf.urls import url
import views
from django.conf.urls import include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'queries', views.QueryViewSet)
router.register(r'jobs', views.JobViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'datasets', views.DatasetViewSet)
router.register(r'databases', views.DatabaseViewSet)
router.register(r'raw', views.RawViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]
