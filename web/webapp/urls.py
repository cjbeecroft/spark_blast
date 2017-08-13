from django.conf.urls import url
from django.contrib import admin
from webapp import views
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import include

urlpatterns = [
    url(r'^jobs/?$', views.JobList.as_view()),
    url(r'^job/(?P<pk>[0-9a-zA-Z\-]+)/$', views.JobDetail.as_view()),
    url(r'^queries/?$', views.QueryList.as_view()),
    url(r'^query/(?P<pk>[0-9a-zA-Z\-]+)/$', views.QueryDetail.as_view()),
    url(r'^users/?$', views.UserList.as_view()),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]