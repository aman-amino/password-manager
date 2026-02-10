from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("app", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserKeyMaterial",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("kdf_salt", models.BinaryField()),
                ("kdf_iterations", models.PositiveIntegerField()),
                ("kdf_alg", models.CharField(default="PBKDF2-HMAC-SHA-256", max_length=64)),
                ("encrypted_user_key", models.BinaryField()),
                (
                    "user",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="key_material", to=settings.AUTH_USER_MODEL),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ScopeKey",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("scope", models.CharField(choices=[("org", "Organization"), ("dept", "Department")], max_length=10)),
                ("key_version", models.PositiveIntegerField(default=1)),
                ("encrypted_scope_key", models.BinaryField()),
                ("is_active", models.BooleanField(default=True)),
                (
                    "department",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="scope_keys", to="app.department"),
                ),
                (
                    "organization",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="scope_keys", to="app.organization"),
                ),
            ],
            options={
                "indexes": [
                    models.Index(fields=["scope", "organization", "department", "is_active"], name="vault_scopek_scope_8f5a5a_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="VaultItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("scope", models.CharField(choices=[("personal", "Personal"), ("org", "Organization"), ("dept", "Department")], max_length=10)),
                ("title", models.CharField(max_length=200)),
                ("item_type", models.CharField(default="generic", max_length=50)),
                ("encrypted_blob", models.BinaryField()),
                ("nonce", models.BinaryField()),
                ("is_favorite", models.BooleanField(default=False)),
                ("is_deleted", models.BooleanField(default=False)),
                (
                    "department",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="vault_items", to="app.department"),
                ),
                (
                    "organization",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="vault_items", to="app.organization"),
                ),
                (
                    "owner",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="vault_items", to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={
                "indexes": [
                    models.Index(fields=["organization", "scope", "is_deleted"], name="vault_vault_organiz_f4a5c1_idx"),
                    models.Index(fields=["owner", "is_deleted"], name="vault_vault_owner_i_16f6d7_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="VaultItemKey",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("wrapped_key", models.BinaryField()),
                ("wrapped_key_alg", models.CharField(default="ECDH-P256+A256GCM", max_length=64)),
                (
                    "recipient",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="received_keys", to=settings.AUTH_USER_MODEL),
                ),
                (
                    "vault_item",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="wrapped_keys", to="vault.vaultitem"),
                ),
            ],
            options={
                "unique_together": {("vault_item", "recipient")},
            },
        ),
    ]
