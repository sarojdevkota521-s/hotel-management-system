
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, status
from .models import User
from apitest.permission import IsAdminUserRole, IsCustomerUser, IsAdminOrStaff, IsEmailVerified
from .serializers import LoginSerializer, UserSerializer, VerifyOTPSerializer, ResendOTPSerializer, ForgotPasswordSerializer, ResetPasswordSerializer, RegisterSerializer
from rest_framework.permissions import IsAuthenticated
IsEmailVerified

# Create your views here.

class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class LoginView(APIView):

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }, status=status.HTTP_200_OK)


# class AdminDashboardView(APIView):
#     permission_classes = [IsAdminUserRole]

#     def get(self, request):
#         return Response({"message": "Welcome Admin"})

# class CustomerView(APIView):
#     permission_classes = [IsCustomerUser]

#     def get(self, request):
#         return Response({"message": "Welcome Customer"})
    
# class CommonView(APIView):
#     permission_classes = [IsAdminOrStaff]

#     def get(self, request):
#         return Response({"message": "Accessible to both"})


class VerifyOTPView(APIView):
    serializer_class = VerifyOTPSerializer
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response({"msg": "Email and OTP are required"}, status=400)

        from .models import User
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"msg": "User not found"}, status=404)

        if user.is_email_verified:
            return Response({"msg": "Email is already verified"}, status=400)

        if user.otp != str(otp):
            return Response({"msg": "Invalid OTP"}, status=400)

        from django.utils import timezone
        if user.otp_expiry and timezone.now() > user.otp_expiry:
            return Response({"msg": "OTP has expired"}, status=400)

        # OTP is valid
        user.is_email_verified = True
        user.otp = None
        user.otp_expiry = None
        user.save()

        return Response({"msg": "Email verified successfully!"}, status=200)

class ResendOTPView(APIView):
    serializer_class = ResendOTPSerializer
    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({"msg": "Email is required"}, status=400)

        from .models import User
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"msg": "User not found"}, status=404)

        if user.is_email_verified:
            return Response({"msg": "Email is already verified"}, status=400)

        import random
        from django.utils import timezone
        from datetime import timedelta
        from django.core.mail import send_mail

        otp = str(random.randint(100000, 999999))
        expiry = timezone.now() + timedelta(minutes=10)

        user.otp = otp
        user.otp_expiry = expiry
        user.save()

        # Send Email
        subject = "Your OTP for Email Verification"
        message = f"Hi {user.name or 'User'},\n\nYour OTP for email verification is: {otp}\nThis OTP is valid for 10 minutes.\n\nBest regards,\nThe Jobryn Team"
        from django.conf import settings
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return Response({"msg": "OTP resent to your email"}, status=200)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated, IsEmailVerified]
    serializer_class = UserSerializer

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ForgotPasswordView(APIView):
    serializer_class = ForgotPasswordSerializer
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"msg": "Email is required"}, status=400)

        from .models import User
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"msg": "User not found"}, status=404)

        import random
        from django.utils import timezone
        from datetime import timedelta
        from django.core.mail import send_mail

        otp = str(random.randint(100000, 999999))
        expiry = timezone.now() + timedelta(minutes=10)

        user.otp = otp
        user.otp_expiry = expiry
        user.save()

        # Send Email
        subject = "Password Reset OTP"
        message = f"Hi {user.name or 'User'},\n\nYour OTP for password reset is: {otp}\nThis OTP is valid for 10 minutes.\n\nBest regards,\nThe Jobryn Team"
        from django.conf import settings
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return Response({"msg": "OTP sent to your email"}, status=200)


class ResetPasswordView(APIView):
    serializer_class = ResetPasswordSerializer
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')

        if not all([email, otp, new_password]):
            return Response({"msg": "Email, OTP, and new password are required"}, status=400)

        from .models import User
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"msg": "User not found"}, status=404)

        if user.otp != str(otp):
            return Response({"msg": "Invalid OTP"}, status=400)

        from django.utils import timezone
        if user.otp_expiry and timezone.now() > user.otp_expiry:
            return Response({"msg": "OTP has expired"}, status=400)

        # OTP is valid, reset password
        user.set_password(new_password)
        user.otp = None
        user.otp_expiry = None
        user.save()

        return Response({"msg": "Password reset successfully"}, status=200)