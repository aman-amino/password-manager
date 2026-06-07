from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404
from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

from app.models import User
from .models import UserKeyMaterial
import base64

class RegisterView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password") # This is AuthKey from client
        salt = request.data.get("salt") # Base64
        iterations = request.data.get("iterations")
        encrypted_user_key = request.data.get("encrypted_user_key") # Base64

        if not all([username, password, salt, iterations, encrypted_user_key]):
            return Response({"error": "Missing fields"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, password=password)
        UserKeyMaterial.objects.create(
            user=user,
            kdf_salt=base64.b64decode(salt),
            kdf_iterations=iterations,
            encrypted_user_key=base64.b64decode(encrypted_user_key)
        )

        return Response({"status": "user created"}, status=status.HTTP_201_CREATED)

class LoginParamsView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        username = request.query_params.get("username")
        if not username:
            return Response({"error": "Username required"}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, username=username)
        material = user.key_material
        return Response({
            "salt": base64.b64encode(material.kdf_salt).decode(),
            "iterations": material.kdf_iterations,
            "encrypted_user_key": base64.b64encode(material.encrypted_user_key).decode()
        })

class LoginView(views.APIView):
    permission_classes = [AllowAny]

    @method_decorator(ensure_csrf_cookie)
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password") # AuthKey

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return Response({"status": "logged in", "username": user.username, "role": user.role})
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"status": "logged out"})

class MeView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "mfa_enabled": user.mfa_enabled
        })

class UserViewSet(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Optimization: select_related reduces O(N) queries to O(1) by joining organization and department.
        users = User.objects.select_related("organization", "department").all()
        if request.user.organization_id:
            users = users.filter(organization_id=request.user.organization_id)

        data = []
        for u in users:
            data.append({
                "username": u.username,
                "email": u.email,
                "role": u.role,
                "organization": u.organization.name if u.organization else None,
                "department": u.department.name if u.department else None
            })
        return Response(data)
