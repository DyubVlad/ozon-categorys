# Generated by Django 3.1.4 on 2020-12-11 21:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('texts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goods',
            name='categoryid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='texts.categorylist'),
        ),
    ]
