# Generated by Django 3.0.3 on 2020-03-02 12:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statechanges', '0002_appstatus'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='statechange',
            options={'ordering': ['block']},
        ),
    ]