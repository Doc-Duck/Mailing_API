from django.db import models
from django.core.validators import RegexValidator


class MailingList(models.Model):
    start_time = models.DateTimeField()
    content = models.TextField()
    codes = models.ManyToManyField('Codes')
    tags = models.ManyToManyField('Tags')
    end_time = models.DateTimeField()


class Client(models.Model):
    phone_regex = RegexValidator(regex=r'7[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]', message='Введите номер в формате "7**********"')
    number = models.BigIntegerField(validators=[phone_regex])
    code = models.ManyToManyField('Codes')
    tags = models.ManyToManyField('Tags')
    timezone = models.CharField(max_length=20, default='Europe/Moscow')


class Message(models.Model):
    created_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100)
    mailingList = models.ForeignKey('MailingList', on_delete=models.CASCADE)
    client = models.ForeignKey('Client', on_delete=models.CASCADE)


class Tags(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Codes(models.Model):
    code = models.IntegerField()

    def __str__(self):
        return str(self.code)