# Generated by Django 4.2.2 on 2023-09-11 21:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("bc_app", "0011_remove_userprofile_added_date"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="ExtendedZenotiEmployeesLeaveData",
            new_name="EmployeesLeaveData",
        ),
        migrations.RemoveField(
            model_name="employeesleavedata",
            name="zenoti_data",
        ),
        migrations.AddField(
            model_name="employeesleavedata",
            name="user_profile",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="bc_app.userprofile",
            ),
        ),
    ]