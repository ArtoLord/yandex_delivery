# Generated by Django 3.1.7 on 2021-03-10 16:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20210310_1545'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='complete_time',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.CreateModel(
            name='Assignation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assign_time', models.DateTimeField(auto_now=True)),
                ('courier', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='assignation', to='app.courier')),
            ],
        ),
        migrations.AlterField(
            model_name='order',
            name='assigned_to',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='app.assignation'),
        ),
    ]
