from rest_framework import serializers
from models import Job
from models import Query
from models import Database
from models import Dataset
from models import Raw
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
    databases = serializers.HyperlinkedRelatedField(
        many=True,
        queryset=Database.objects.all(),
        required=True,
        view_name='database-detail'
    )

    class Meta:
        model = Job
        fields = ('id', 'url', 'name', 'yarn_id', 'status', 'query', 'databases', 'start_time', 'end_time',)

class JobListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Job
        fields = ('id', 'url', 'name', 'status', 'start_time', 'end_time', 'query' )

class DatasetSerializer(serializers.ModelSerializer):
    #jobs = serializers.HyperlinkedRelatedField(
    #    many=True,
    #    queryset=Job.objects.all(),
    #    required=False,
    #    view_name='job-detail'
    #)
    raw_data = serializers.StringRelatedField(many=True, required=False)

    class Meta:
        model = Dataset
        fields = ('name', 'url', 'created', 'raw_data')

class DatabaseSerializer(serializers.ModelSerializer):
    jobs = serializers.HyperlinkedRelatedField(
        many=True,
        queryset=Job.objects.all(),
        required=False,
        view_name='job-detail'
    )
    datasets = serializers.HyperlinkedRelatedField(
        many=True,
        queryset=Dataset.objects.all(),
        required=True,
        view_name='dataset-detail'
    )
    raw_data = serializers.StringRelatedField(many=True, required=False)

    class Meta:
        model = Database
        fields = ('name', 'url', 'created', 'jobs', 'datasets', 'raw_data')

class RawSerializer(serializers.ModelSerializer):

    class Meta:
        model = Raw
        fields = ('id', 'dataset','database','location', 'url')

class UserSerializer(serializers.ModelSerializer):
    users_queries = serializers.PrimaryKeyRelatedField(many=True, queryset=Query.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'users_queries')
