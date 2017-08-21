from rest_framework import serializers
from webapp.models import Job
from webapp.models import Query
from webapp.models import Dataset
from webapp.models import Raw
from django.db.models import UUIDField
from django.contrib.auth.models import User


class QuerySerializer(serializers.ModelSerializer):
    #url = serializers.HyperlinkedIdentityField(view_name='query_detail')
    jobs = serializers.HyperlinkedRelatedField(
        many=True,
        queryset=Job.objects.all(),
        required=False,
        view_name='job-detail'
    )
    creator = serializers.ReadOnlyField(source='creator.username')

    class Meta:
        model = Query
        fields = ('id', 'url', 'name', 'sequence', 'created', 'creator', 'jobs')


class JobSerializer(serializers.ModelSerializer):
    datasets = serializers.HyperlinkedRelatedField(
        many=True,
        queryset=Dataset.objects.all(),
        required=True,
        view_name='dataset-detail'
    )

    class Meta:
        model = Job
        fields = ('id', 'url', 'name', 'yarn_id', 'status', 'query', 'datasets', 'start_time', 'end_time',  )

class JobListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Job
        fields = ('id', 'url', 'name', 'status', 'start_time', 'end_time', 'query' )

class DatasetSerializer(serializers.ModelSerializer):
    jobs = serializers.HyperlinkedRelatedField(
        many=True,
        queryset=Job.objects.all(),
        required=False,
        view_name='job-detail'
    )
    raw_data = serializers.StringRelatedField(many=True, required=False)

    class Meta:
        model = Dataset
        fields = ('name', 'url', 'created', 'jobs', 'raw_data')

class RawSerializer(serializers.ModelSerializer):

    class Meta:
        model = Raw
        fields = ('id', 'dataset','location', 'url')

class UserSerializer(serializers.ModelSerializer):
    users_queries = serializers.PrimaryKeyRelatedField(many=True, queryset=Query.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'users_queries')
