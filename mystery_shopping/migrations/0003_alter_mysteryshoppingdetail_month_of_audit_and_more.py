# Generated by Django 4.2.2 on 2023-08-21 20:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("bc_app", "0009_remove_centralaccess_audit_and_more"),
        ("mystery_shopping", "0002_mysteryshoppingoverview_auditor_access_to"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mysteryshoppingdetail",
            name="month_of_audit",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="bc_app.monthaudit",
            ),
        ),
        migrations.AlterField(
            model_name="mysteryshoppingoverview",
            name="month_of_audit",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="bc_app.monthaudit",
            ),
        ),
        migrations.DeleteModel(
            name="MonthAudit",
        ),
    ]
