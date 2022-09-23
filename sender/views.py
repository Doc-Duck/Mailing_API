import threading

import requests
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.utils import timezone
import dateutil.parser as parser
from .serializers import *
from .models import MailingList
from rest_framework import generics


class MailListView(generics.ListCreateAPIView):
    queryset = MailingList.objects.all()
    serializer_class = MailingListSerializer

    def post(self, request, *args, **kwargs):
        codes = [Codes.objects.get(code=item) for item in request.data['codes']]
        tags = [Tags.objects.get(name=item) for item in request.data['tags']]
        start_time = request.data['start_time']
        end_time = request.data['end_time']
        content = request.data['content']
        ml = MailingList(start_time=start_time, end_time=end_time, content=content)
        ml.save()
        ml.tags.set(tags)
        ml.codes.set(codes)
        serializer = self.get_serializer(ml)
        tm_s = parser.parse(ml.start_time)
        tm_e = parser.parse(ml.end_time)
        if tags and not codes:
            client_list = Client.objects.filter(tags__in=ml.tags.all()).distinct()
        elif codes and not tags:
            client_list = Client.objects.filter(code__in=ml.codes.all()).distinct()
        elif codes and tags:
            client_list = Client.objects.filter(tags__in=ml.tags.all(), code__in=ml.codes.all()).distinct()
        else:
            client_list = Client.objects.all()
        if tm_s <= timezone.localtime(timezone.now()) <= tm_e:
            th = threading.Thread(target=make_mails, args=(client_list, content, ml))
            th.start()
        else:
            delay = (tm_s - timezone.localtime(timezone.now())).total_seconds()
            print(delay)
            threading.Timer(delay, make_mails, args=(client_list, content, ml)).start()

        return Response(serializer.data, status=status.HTTP_200_OK)


class MailListDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = MailingList.objects.all()
    serializer_class = MailingListSerializer

    def partial_update(self, request, *args, **kwargs):
        ml = self.get_object()
        data = request.data

        ml.start_time = data.get('start_time', ml.start_time)
        ml.content = data.get('content', ml.content)
        ml.end_time = data.get('end_time', ml.end_time)
        if data['codes']:
            ml.codes = Codes.objects.get(code=data['codes'])
        if data['tags']:
            tags = [Tags.objects.get(name=item) for item in request.data['tags']]
            ml.tags.set(tags)
        ml.save()
        serializer = self.get_serializer(ml)

        return Response(serializer.data)


class ClientListView(generics.ListCreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    def post(self, request, *args, **kwargs):
        code = Codes.objects.get(code=request.data['code'])
        tags = [Tags.objects.get(name=item) for item in request.data['tags']]
        number = request.data['number']
        timezone = request.data['timezone']
        ml = Client(number=number, timezone=timezone, code=code)
        ml.save()
        ml.tags.set(tags)
        serializer = self.get_serializer(ml)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ClientDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    def partial_update(self, request, *args, **kwargs):
        ml = self.get_object()
        data = request.data

        ml.number = data.get('number', ml.number)
        ml.timezone = data.get('timezone', ml.timezone)
        if data['code']:
            ml.code = Codes.objects.get(code=request.data['code'])
        if data['tags']:
            tags = [Tags.objects.get(name=item) for item in request.data['tags']]
            ml.tags.set(tags)
        ml.save()
        serializer = self.get_serializer(ml)

        return Response(serializer.data)


class MailingListStats(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        lst = Message.objects.filter(id=kwargs['ml_id']).count()
        ok = Message.objects.filter(id=kwargs['ml_id'], status='OK').count()
        return Response({'total_messages': lst, 'delivered': ok})


class AllMessagesStats(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        try:
            lst = Message.objects.get(status=kwargs['status'])
        except:
            lst = Message.objects.filter(status=kwargs['status'])
        serializer = MessagesSerializer(lst, many=True)
        return Response(serializer.data)


def sending_data(id, phone, content, ml, client):
    auth_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2OTQ2OTgzOTAsImlzcyI6ImZhYnJpcXVlIiwibmFtZSI6IlByb3N0b3V0eWEifQ.A7ZQl-iwaoo8PzKLt3a7r0VVWHFD5nz-tbYVDo7rJSQ'
    hed = {'Authorization': 'Bearer ' + auth_token}
    data = {"id": id,
            "phone": phone,
            "text": content}

    url = f'https://probe.fbrq.cloud/v1/send/{id}'
    response = requests.post(url, json=data, headers=hed)
    print(response.json())
    msg = Message(status=response.json()['message'], mailingList=ml, client=client)
    msg.save()


def make_mails(client_list, content, ml):
    for client in client_list:
        try:
            last_msg_id = Message.objects.last().id
        except:
            last_msg_id = 1
        my_thread = threading.Thread(target=sending_data, args=(last_msg_id + 1, client.number, content, ml, client))
        my_thread.start()