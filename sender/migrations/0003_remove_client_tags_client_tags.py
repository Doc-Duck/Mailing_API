# Generated by Django 4.1.1 on 2022-09-17 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sender', '0002_remove_mailinglist_tags_mailinglist_tags'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='tags',
        ),
        migrations.AddField(
            model_name='client',
            name='tags',
            field=models.ManyToManyField(to='sender.tags'),
        ),
    ]
