# Generated by Django 4.2.2 on 2023-10-04 20:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("bc_app", "0011_userprofile_associated_location"),
        ("roster", "0002_alter_employeeroster_employee_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="employeeroster",
            name="associated_role",
        ),
        migrations.RemoveField(
            model_name="employeescheduler",
            name="associated_role",
        ),
        migrations.AddField(
            model_name="employeeroster",
            name="associated_kra",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="bc_app.centerkra",
            ),
        ),
        migrations.AddField(
            model_name="employeescheduler",
            name="associated_kra",
            field=models.ManyToManyField(blank=True, to="bc_app.centerkra"),
        ),
    ]
