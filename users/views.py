from rest_framework import generics, permissions, status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from .serializers import UserRegisterSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegisterSerializer


class PenaltyPointsView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        user = None
        # Allow admin or self access only
        if request.user.is_staff or request.user.id == int(pk):
            try:
                user = User.objects.get(pk=pk)
            except User.DoesNotExist:
                return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
            return Response({"user_id": user.id, "penalty_points": user.penalty_points})
        else:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
