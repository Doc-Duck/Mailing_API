from rest_framework.serializers import ModelSerializer
from .models import *


class MailingListSerializer(ModelSerializer):
    class Meta:
        depth = 1
        model = MailingList
        fields = ['start_time', 'content', 'codes', 'tags', 'end_time']


class ClientSerializer(ModelSerializer):
    class Meta:
        depth = 1
        model = Client
        fields = ['number', 'code', 'tags', 'timezone']


class MessagesSerializer(ModelSerializer):
    class Meta:
        depth = 1
        model = Message
        fields = ['created_time', 'status', 'mailingList', 'client']
