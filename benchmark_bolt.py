import os
import django
import timeit
import base64

from django.conf import settings

if not settings.configured:
    settings.configure(
        DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}},
        INSTALLED_APPS=['django.contrib.contenttypes', 'django.contrib.auth', 'vault', 'app'],
    )
    django.setup()

from rest_framework import serializers
from vault.models import VaultItem

class OptimizedSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaultItem
        fields = ['encrypted_blob', 'nonce']
        extra_kwargs = {
            'encrypted_blob': {'read_only': False},
            'nonce': {'read_only': False}
        }

class SlowSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaultItem
        fields = ['encrypted_blob', 'nonce']
        extra_kwargs = {
            'encrypted_blob': {'read_only': False},
            'nonce': {'read_only': False}
        }
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if ret.get('encrypted_blob'):
            ret['encrypted_blob'] = base64.b64encode(instance.encrypted_blob).decode()
        if ret.get('nonce'):
            ret['nonce'] = base64.b64encode(instance.nonce).decode()
        return ret

# Prepare data
blob = os.urandom(1024 * 100) # 100KB
nonce = os.urandom(12)
item = VaultItem(encrypted_blob=blob, nonce=nonce)

def test_optimized():
    OptimizedSerializer(instance=item).data

def test_slow():
    SlowSerializer(instance=item).data

t_opt = timeit.timeit(test_optimized, number=1000)
t_slow = timeit.timeit(test_slow, number=1000)

print(f"Optimized: {t_opt:.4f}s")
print(f"Slow: {t_slow:.4f}s")
print(f"Improvement: {(t_slow - t_opt) / t_slow * 100:.2f}%")
