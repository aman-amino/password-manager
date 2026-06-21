import base64
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from .models import VaultItem, AuditEvent, AccessGrant
from .policy import can_create_vault_item

class VaultItemSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = VaultItem
        fields = [
            "id",
            "owner",
            "organization",
            "department",
            "scope",
            "title",
            "item_type",
            "encrypted_blob",
            "nonce",
            "is_favorite",
            "is_deleted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "organization", "department", "created_at", "updated_at"]
        # Bolt Optimization: In DRF 3.16.1+, BinaryField properties are read-only by default.
        # Setting read_only: False enables automatic Base64 encoding/decoding, which is faster
        # than manual base64.b64encode/decode calls.
        extra_kwargs = {
            "encrypted_blob": {"read_only": False},
            "nonce": {"read_only": False},
        }

    def validate_encrypted_blob(self, value):
        # Bolt Optimization: value is already decoded to bytes/memoryview by DRF.
        MAX_SIZE = 1 * 1024 * 1024
        if len(value) > MAX_SIZE:
            raise serializers.ValidationError("Encrypted blob exceeds 1MB limit.")
        return value

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user
        scope = attrs.get("scope") or getattr(self.instance, "scope", None)

        decision = can_create_vault_item(user, scope)
        if not decision.allowed:
            raise serializers.ValidationError(f"Permission denied for scope '{scope}': {decision.reason}")

        return attrs

    def create(self, validated_data):
        # Bolt Optimization: Use IDs directly to avoid redundant database lookups for Organization and Department objects.
        user = self.context["request"].user
        validated_data["owner"] = user
        validated_data["organization_id"] = user.organization_id
        validated_data["department_id"] = user.department_id
        return super().create(validated_data)

class AuditEventSerializer(serializers.ModelSerializer):
    actor = serializers.StringRelatedField()
    class Meta:
        model = AuditEvent
        fields = '__all__'

class AccessGrantSerializer(serializers.ModelSerializer):
    grantee_username = serializers.CharField(write_only=True)
    grantee = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = AccessGrant
        fields = ["id", "vault_item", "grantee", "grantee_username", "granted_by", "expires_at", "is_active"]
        read_only_fields = ["id", "granted_by", "grantee"]

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user
        item = attrs.get("vault_item")

        from .policy import can_manage_vault_item
        decision = can_manage_vault_item(user, item)
        if not decision.allowed:
            raise serializers.ValidationError(f"Permission denied: You cannot grant access to this item. {decision.reason}")

        return attrs

    def create(self, validated_data):
        username = validated_data.pop("grantee_username")
        from app.models import User
        grantee = get_object_or_404(User, username=username)
        validated_data["grantee"] = grantee
        validated_data["granted_by"] = self.context["request"].user
        return super().create(validated_data)
