# Generated by Django 3.1.7 on 2021-03-06 07:53

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Region',
            fields=[
                ('region_id', models.IntegerField(primary_key=True, serialize=False, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_id', models.IntegerField(primary_key=True, serialize=False, unique=True)),
                ('weight', models.FloatField()),
                ('delivery_hours', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=16), size=None)),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='app.region')),
            ],
        ),
        migrations.CreateModel(
            name='Courier',
            fields=[
                ('courier_id', models.IntegerField(primary_key=True, serialize=False, unique=True)),
                ('courier_type', models.CharField(choices=[('foot', 'Foot'), ('bike', 'Bike'), ('car', 'Car')], max_length=4)),
                ('working_hours', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=16), size=None)),
                ('rating', models.FloatField()),
                ('earnings', models.IntegerField()),
                ('regions', models.ManyToManyField(related_name='couriers', to='app.Region')),
            ],
        ),
    ]