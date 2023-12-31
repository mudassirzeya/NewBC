# Generated by Django 4.2.2 on 2023-10-05 08:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("bc_app", "0011_userprofile_associated_location"),
        ("roster", "0003_remove_employeeroster_associated_role_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="employeeroster",
            name="associated_location",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="bc_app.location",
            ),
        ),
        migrations.AddField(
            model_name="employeescheduler",
            name="associated_location",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="bc_app.location",
            ),
        ),
        migrations.AlterField(
            model_name="employeeroster",
            name="associated_kra",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="bc_app.kra",
            ),
        ),
        migrations.RemoveField(
            model_name="employeescheduler",
            name="associated_kra",
        ),
        migrations.AddField(
            model_name="employeescheduler",
            name="associated_kra",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="bc_app.kra",
            ),
        ),
    ]
