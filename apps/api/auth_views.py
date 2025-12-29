"""
Authentication API views for QuietPage.

This module provides REST API endpoints for user authentication including:
- Login (username or email)
- Logout
- Registration
- Current user info
- CSRF token retrieval
"""

from django.contrib.auth import authenticate, login, logout, get_user_model
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.auth_serializers import LoginSerializer, RegisterSerializer
from apps.api.serializers import UserSerializer

User = get_user_model()


class LoginView(APIView):
    """
    API endpoint for user login.

    Accepts username or email along with password.
    Returns user data and sets session cookie on success.

    POST /api/v1/auth/login/
    Request: {"username_or_email": "...", "password": "..."}
    Response 200: {"user": {...}}
    Response 400: {"error": "Invalid credentials"}
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        username_or_email = serializer.validated_data['username_or_email']
        password = serializer.validated_data['password']

        # Determine if input is email or username
        user = None
        if '@' in username_or_email:
            # Input looks like email
            try:
                user_obj = User.objects.get(email__iexact=username_or_email)
                username = user_obj.username
            except User.DoesNotExist:
                username = None
        else:
            # Input is username
            username = username_or_email

        # Authenticate with username (authenticate() requires username field)
        if username:
            user = authenticate(
                request=request,
                username=username,
                password=password
            )

        if user is None:
            return Response(
                {'error': 'Neplatné přihlašovací údaje.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user account is active
        if not user.is_active:
            return Response(
                {'error': 'Tento účet byl deaktivován.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Log the user in (creates session)
        login(request, user)

        # Return user data
        user_serializer = UserSerializer(user, context={'request': request})
        return Response(
            {'user': user_serializer.data},
            status=status.HTTP_200_OK
        )


class LogoutView(APIView):
    """
    API endpoint for user logout.

    Destroys the user session.
    No authentication required (can logout even if session is invalid).

    POST /api/v1/auth/logout/
    Response 200: {"message": "Logged out successfully"}
    """
    permission_classes = [AllowAny]

    def post(self, request):
        logout(request)
        return Response(
            {'message': 'Úspěšně odhlášeno.'},
            status=status.HTTP_200_OK
        )


class RegisterView(APIView):
    """
    API endpoint for user registration.

    Creates a new user account and automatically logs them in.
    Validates username/email uniqueness and password strength.

    POST /api/v1/auth/register/
    Request: {
        "username": "...",
        "email": "...",
        "password": "...",
        "password_confirm": "..."
    }
    Response 201: {"user": {...}}
    Response 400: {"errors": {...}}
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the user
        user = serializer.save()

        # Automatically log in the new user
        login(request, user)

        # Return user data
        user_serializer = UserSerializer(user, context={'request': request})
        return Response(
            {'user': user_serializer.data},
            status=status.HTTP_201_CREATED
        )


class CurrentUserView(APIView):
    """
    API endpoint to get current authenticated user data.

    Returns user information for the currently logged-in user.
    Requires authentication.

    GET /api/v1/auth/me/
    Response 200: {"user": {...}}
    Response 401: {"detail": "Authentication credentials were not provided."}
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(
            {'user': serializer.data},
            status=status.HTTP_200_OK
        )


class CSRFTokenView(APIView):
    """
    API endpoint to retrieve CSRF token.

    Returns a CSRF token for use in subsequent requests.
    This endpoint is public and sets the CSRF cookie.

    GET /api/v1/auth/csrf/
    Response 200: {"csrfToken": "..."}
    """
    permission_classes = [AllowAny]

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        # Get CSRF token for this session
        csrf_token = get_token(request)

        return Response(
            {'csrfToken': csrf_token},
            status=status.HTTP_200_OK
        )
