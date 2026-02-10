from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("vault", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Tag",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=100)),
                ("kind", models.CharField(choices=[("system", "System"), ("personal", "Personal")], max_length=20)),
                (
                    "owner",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="tags", to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={"unique_together": {("name", "kind", "owner")}},
        ),
        migrations.CreateModel(
            name="VaultItemTag",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "tag",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="vault_links", to="vault.tag"),
                ),
                (
                    "vault_item",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="tag_links", to="vault.vaultitem"),
                ),
            ],
            options={"unique_together": {("vault_item", "tag")}},
        ),
        migrations.CreateModel(
            name="AccessGrant",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "granted_by",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="grants_given", to=settings.AUTH_USER_MODEL),
                ),
                (
                    "grantee",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="access_grants", to=settings.AUTH_USER_MODEL),
                ),
                (
                    "vault_item",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="access_grants", to="vault.vaultitem"),
                ),
            ],
            options={"unique_together": {("vault_item", "grantee")}},
        ),
        migrations.CreateModel(
            name="RecoveryKey",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("public_key", models.BinaryField()),
                ("wrapped_recovery_key", models.BinaryField()),
                (
                    "user",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="recovery_key", to=settings.AUTH_USER_MODEL),
                ),
            ],
        ),
        migrations.CreateModel(
            name="AuditEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("target_type", models.CharField(max_length=50)),
                ("target_id", models.CharField(max_length=64)),
                ("action", models.CharField(choices=[("read", "Read"), ("create", "Create"), ("update", "Update"), ("delete", "Delete"), ("login", "Login"), ("admin", "Admin")], max_length=20)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                (
                    "actor",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="audit_events", to=settings.AUTH_USER_MODEL),
                ),
                (
                    "organization",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="audit_events", to="app.organization"),
                ),
            ],
            options={
                "indexes": [
                    models.Index(fields=["organization", "created_at"], name="vault_audite_organiz_42f2c2_idx"),
                    models.Index(fields=["actor", "created_at"], name="vault_audite_actor_i_07d13d_idx"),
                ],
            },
        ),
    ]
