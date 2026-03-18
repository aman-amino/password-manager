from rest_framework import serializers

from .models import VaultItem


class VaultItemSerializer(serializers.ModelSerializer):
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

    def validate_encrypted_blob(self, value):
        # Limit encrypted blob to 1MB to prevent potential DoS/storage exhaustion
        MAX_SIZE = 1 * 1024 * 1024  # 1MB
        if len(value) > MAX_SIZE:
            raise serializers.ValidationError("Encrypted blob exceeds 1MB limit.")
        return value

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user
        scope = attrs.get("scope") or getattr(self.instance, "scope", None)
        if scope == VaultItem.Scope.PERSONAL and user is not None:
            return attrs
        if scope == VaultItem.Scope.ORG and user.organization_id is None:
            raise serializers.ValidationError("Organization scope requires user organization.")
        if scope == VaultItem.Scope.DEPT and user.department_id is None:
            raise serializers.ValidationError("Department scope requires user department.")
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["owner"] = user
        validated_data["organization"] = user.organization
        validated_data["department"] = user.department
        return super().create(validated_data)
