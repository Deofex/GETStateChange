# Generated by Django 3.0.3 on 2020-02-07 13:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Block',
            fields=[
                ('blocknumber', models.IntegerField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField()),
                ('fullyprocessed', models.BooleanField(default=False)),
                ('f0sum', models.IntegerField(default=0)),
                ('f1sum', models.IntegerField(default=0)),
                ('f2sum', models.IntegerField(default=0)),
                ('f3sum', models.IntegerField(default=0)),
                ('f4sum', models.IntegerField(default=0)),
                ('f5sum', models.IntegerField(default=0)),
                ('f6sum', models.IntegerField(default=0)),
                ('f7sum', models.IntegerField(default=0)),
                ('f8sum', models.IntegerField(default=0)),
                ('f9sum', models.IntegerField(default=0)),
                ('f10sum', models.IntegerField(default=0)),
                ('f11sum', models.IntegerField(default=0)),
                ('f12sum', models.IntegerField(default=0)),
                ('f13sum', models.IntegerField(default=0)),
                ('wsum', models.IntegerField(default=0)),
                ('totalsum', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='BurnTransaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('blocknumber', models.IntegerField()),
                ('getburned', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='CryptoPrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=3)),
                ('price_eur', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('hash', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=100)),
                ('f0sum', models.IntegerField(default=0)),
                ('f1sum', models.IntegerField(default=0)),
                ('f2sum', models.IntegerField(default=0)),
                ('f3sum', models.IntegerField(default=0)),
                ('f4sum', models.IntegerField(default=0)),
                ('f5sum', models.IntegerField(default=0)),
                ('f6sum', models.IntegerField(default=0)),
                ('f7sum', models.IntegerField(default=0)),
                ('f8sum', models.IntegerField(default=0)),
                ('f9sum', models.IntegerField(default=0)),
                ('f10sum', models.IntegerField(default=0)),
                ('f11sum', models.IntegerField(default=0)),
                ('f12sum', models.IntegerField(default=0)),
                ('f13sum', models.IntegerField(default=0)),
                ('totalsum', models.IntegerField(default=0)),
                ('block', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='statechanges.Block')),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('hash', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='statechanges.Event')),
            ],
        ),
        migrations.CreateModel(
            name='StateChange',
            fields=[
                ('hash', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('previoushash', models.CharField(max_length=100)),
                ('firing', models.IntegerField(choices=[(0, 'Ticket or Wiring created'), (1, 'Ticket blocked'), (2, 'Ticket sold on primary market'), (3, 'Ticket sold on secondary market'), (4, 'Ticket bought back by organizer'), (5, 'Ticket cancelled'), (6, 'Ticket put for sale'), (7, 'Show cancelled'), (8, 'Ticket not resold'), (9, 'Ticket not sold on primary market'), (10, 'Ticket sold on the secondary market'), (11, 'Ticket scanned'), (12, 'Show over'), (13, 'Ticket unblocked')])),
                ('block', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='statechanges.Block')),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='statechanges.Ticket')),
            ],
        ),
    ]
