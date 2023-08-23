# Generated by Django 4.2.2 on 2023-08-14 17:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("bc_app", "0005_userprofile_is_audit_admin"),
    ]

    operations = [
        migrations.CreateModel(
            name="CentralAccess",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "audit",
                    models.CharField(
                        blank=True,
                        choices=[("SLR Salon", "SLR Salon")],
                        max_length=200,
                        null=True,
                    ),
                ),
                (
                    "audit_reviewer",
                    models.ManyToManyField(
                        blank=True,
                        related_name="audit_reviewer_of",
                        to="bc_app.extendedzenoticenterdata",
                    ),
                ),
                (
                    "auditor",
                    models.ManyToManyField(
                        blank=True,
                        related_name="auditor_of",
                        to="bc_app.extendedzenoticenterdata",
                    ),
                ),
                (
                    "project_manager",
                    models.ManyToManyField(
                        blank=True,
                        related_name="project_manager_of",
                        to="bc_app.extendedzenoticenterdata",
                    ),
                ),
                (
                    "senior_management",
                    models.ManyToManyField(
                        blank=True,
                        related_name="senior_management_of",
                        to="bc_app.extendedzenoticenterdata",
                    ),
                ),
                (
                    "staff",
                    models.ForeignKey(
                        blank=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="bc_app.userprofile",
                    ),
                ),
            ],
        ),
    ]