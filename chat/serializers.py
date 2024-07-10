#chat/serializers.py
from rest_framework import serializers
from .models import Talk

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Talk
        fields = ['id', 'story', 'user', 'text']
