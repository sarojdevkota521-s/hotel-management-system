from django.shortcuts import render
from .models import User
from .serializers import UserSerializer, LoginSerializer
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

# Create your views here.

class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class LoginView(APIView):

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username
            },
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }, status=status.HTTP_200_OK)
    
from rest_framework.views import APIView
from .permission import IsAdminUserRole, IsCustomerUser, IsAdminOrCustomer

class AdminDashboardView(APIView):
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        return Response({"message": "Welcome Admin"})

class CustomerView(APIView):
    permission_classes = [IsCustomerUser]

    def get(self, request):
        return Response({"message": "Welcome Customer"})
    
class CommonView(APIView):
    permission_classes = [IsAdminOrCustomer]

    def get(self, request):
        return Response({"message": "Accessible to both"})