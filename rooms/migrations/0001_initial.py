# Generated by Django 3.0.4 on 2020-04-23 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bookings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booker', models.CharField(max_length=20)),
                ('contact', models.CharField(max_length=20)),
                ('room_name', models.CharField(max_length=20)),
                ('start', models.IntegerField(max_length=4)),
                ('end', models.IntegerField(max_length=4)),
                ('date', models.CharField(max_length=10)),
                ('duration', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Rooms',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
            ],
        ),
    ]