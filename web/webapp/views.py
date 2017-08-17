# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from serializers import UserSerializer
from django.contrib.auth.models import User
from models import Job
from models import Query
from models import Dataset
from models import Raw
from serializers import JobSerializer
from serializers import JobListSerializer
from serializers import QuerySerializer
from serializers import DatasetSerializer
from serializers import RawSerializer
from rest_framework import permissions
from permissions import IsOwnerOrReadOnly
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('users', request=request, format=format),
        'queries': reverse('queries', request=request, format=format)
    })

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.action == 'list':
            return JobListSerializer
        else:
            return JobSerializer

class QueryViewSet(viewsets.ModelViewSet):
    queryset = Query.objects.all()
    serializer_class = QuerySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
    IsOwnerOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def get_queryset(self):
        user = self.request.user
        return Query.objects.filter(creator=user)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class DatasetViewSet(viewsets.ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

class RawViewSet(viewsets.ModelViewSet):
    queryset = Raw.objects.all()
    serializer_class = RawSerializer

