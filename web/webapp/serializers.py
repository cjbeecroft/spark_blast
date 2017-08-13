from rest_framework import serializers
from webapp.models import Job
from webapp.models import Query
from django.db.models import UUIDField
from django.contrib.auth.models import User


class QuerySerializer(serializers.ModelSerializer):
    #url = serializers.HyperlinkedIdentityField(view_name='query_detail')
    jobs = serializers.PrimaryKeyRelatedField(many=True, queryset=Job.objects.all(), required=False)
    creator = serializers.ReadOnlyField(source='creator.username')

    class Meta:
        model = Query
        fields = ('id', 'url', 'name', 'sequence', 'created', 'creator', 'jobs')


class JobSerializer(serializers.ModelSerializer):
    #job = serializers.HyperlinkedIdentityField(view_name='job_detail')

    class Meta:
        model = Job
        fields = ('id', 'url', 'name', 'status', 'location', 'start_time', 'end_time', 'query' )

class UserSerializer(serializers.ModelSerializer):
    users_queries = serializers.PrimaryKeyRelatedField(many=True, queryset=Query.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'users_queries')
