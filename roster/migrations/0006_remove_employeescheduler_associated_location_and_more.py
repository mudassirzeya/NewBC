# Generated by Django 4.2.2 on 2023-10-08 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bc_app", "0011_userprofile_associated_location"),
        ("roster", "0005_remove_employeescheduler_associated_kra_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="employeescheduler",
            name="associated_location",
        ),
        migrations.AddField(
            model_name="employeescheduler",
            name="associated_location",
            field=models.ManyToManyField(blank=True, to="bc_app.location"),
        ),
    ]
