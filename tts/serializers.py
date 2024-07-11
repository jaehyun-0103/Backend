# tts/serializers.py
from rest_framework import serializers

class TtsRequestSerializer(serializers.Serializer):
    sentence = serializers.CharField(max_length=500)
