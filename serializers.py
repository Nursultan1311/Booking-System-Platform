# applications/serializers.py
from django.db.models import Sum
from rest_framework import serializers
from .models import Application, Document, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone_number']


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone_number']

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'


class ApplicationSerializer(serializers.ModelSerializer):
    documents = DocumentSerializer(many=True, read_only=True)
    total_score = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = ['id', 'user', 'documents', 'total_score']

    def get_total_score(self, obj):
        return obj.documents.filter(status='approved').aggregate(total_score=Sum('score'))['total_score'] or 0

