# Generated by Django 3.0.3 on 2020-02-21 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statechanges', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppStatus',
            fields=[
                ('name', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('status', models.BooleanField()),
            ],
        ),
    ]
