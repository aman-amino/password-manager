from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="Organization",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=200, unique=True)),
                ("slug", models.SlugField(max_length=200, unique=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="Department",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=200)),
                ("slug", models.SlugField(max_length=200)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "organization",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="departments", to="app.organization"),
                ),
            ],
            options={"unique_together": {("organization", "slug")}},
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("is_superuser", models.BooleanField(default=False, help_text="Designates that this user has all permissions.", verbose_name="superuser status")),
                ("username", models.CharField(max_length=150, unique=True, verbose_name="username")),
                ("first_name", models.CharField(blank=True, max_length=150, verbose_name="first name")),
                ("last_name", models.CharField(blank=True, max_length=150, verbose_name="last name")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="email address")),
                ("is_staff", models.BooleanField(default=False, help_text="Designates whether the user can log into this admin site.", verbose_name="staff status")),
                ("is_active", models.BooleanField(default=True, help_text="Designates whether this user should be treated as active.", verbose_name="active")),
                ("date_joined", models.DateTimeField(auto_now_add=True, verbose_name="date joined")),
                ("role", models.CharField(choices=[("superadmin", "Superadmin"), ("admin", "Admin"), ("subadmin", "Subadmin"), ("user", "User")], default="user", max_length=20)),
                ("mfa_enabled", models.BooleanField(default=False)),
                (
                    "department",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="users", to="app.department"),
                ),
                (
                    "organization",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="users", to="app.organization"),
                ),
                (
                    "groups",
                    models.ManyToManyField(blank=True, help_text="The groups this user belongs to.", related_name="user_set", to="auth.group", verbose_name="groups"),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(blank=True, help_text="Specific permissions for this user.", related_name="user_set", to="auth.permission", verbose_name="user permissions"),
                ),
            ],
            options={"abstract": False},
        ),
    ]
