# Generated by Django 4.2.2 on 2023-10-01 12:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("bc_app", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="employeeroster",
            name="associated_kra",
        ),
        migrations.RemoveField(
            model_name="employeescheduler",
            name="associated_kra",
        ),
        migrations.RemoveField(
            model_name="extendedzenoticenterdata",
            name="associated_kra",
        ),
        migrations.RemoveField(
            model_name="extendedzenotiemployeesdata",
            name="associated_kra",
        ),
        migrations.RemoveField(
            model_name="userprofile",
            name="associated_kra",
        ),
        migrations.DeleteModel(
            name="KRA",
        ),
    ]