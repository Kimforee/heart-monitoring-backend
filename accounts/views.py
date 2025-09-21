# accounts/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .serializers import RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    """
    POST /api/accounts/register/
    Registers a new user.
    """

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        """
        Overriding to return a serialized user (without password) on success.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        read = UserSerializer(user, context={"request": request})
        return Response(read.data, status=status.HTTP_201_CREATED)


class ProfileView(generics.RetrieveAPIView):
    """
    GET /api/accounts/me/ -> returns current user details
    """

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
