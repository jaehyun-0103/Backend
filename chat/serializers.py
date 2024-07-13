# chat/serializers.py
from rest_framework import serializers

class GPTChatSerializer(serializers.Serializer):
    gpt_message = serializers.CharField()
