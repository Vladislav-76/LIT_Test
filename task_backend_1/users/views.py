from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from djoser import signals
from djoser.compat import get_user_email
from djoser.views import UserViewSet
from drf_yasg.utils import swagger_auto_schema
from pyotp import TOTP, random_base32
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from templated_mail.mail import BaseEmailMessage
from users import tasks
from users.serializers import OtpSerializer

User = get_user_model()

users_otp = dict()


def get_otp_code(user):
    """Generating and saving the otp code and the time it was created."""

    otp_code = TOTP(random_base32(), digits=settings.OTP_LENTH).now()
    users_otp[user.id] = {'otp_code': otp_code, 'otp_created': timezone.now()}
    return otp_code


def get_context(request, otp_code):
    """Getting context for email template filling."""

    email = BaseEmailMessage(request)
    context = email.get_context_data()
    context.pop('view', None)
    context.pop('user', None)
    context.update({'otp_code': otp_code, 'template_name': settings.OTP_EMAIL_TEMPLATE})
    return context


class OtpUserViewSet(UserViewSet):
    def perform_create(self, serializer, *args, **kwargs):
        """Custom POST User method with sending email with OTP-code."""

        user = serializer.save(*args, **kwargs)
        signals.user_registered.send(sender=self.__class__, user=user, request=self.request)
        otp_code = get_otp_code(user)
        to = [get_user_email(user)]
        tasks.send_otp_activation.delay(get_context(self.request, otp_code), to)


class OtpActivateView(APIView):
    """User activation, only POST."""

    @swagger_auto_schema(
        operation_description='Set User is_active if OTP is valid',
        request_body=OtpSerializer,
        responses={200: OtpSerializer, 400: OtpSerializer}
    )
    def post(self, request):
        serializer = OtpSerializer(data=request.data)
        if serializer.is_valid():
            user = get_object_or_404(User, email=request.data['email'])
            user.is_active = True
            user.save()
            users_otp.pop(user.id, None)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)


class OtpObtainView(APIView):
    """Getting OTP-code."""

    sucsess_response = 'OTP successfully sent by email'
    unauthorized = 'No active account found with the given credentials'

    @swagger_auto_schema(
        operation_description='Getting OTP-code',
        request_body=TokenObtainSerializer,
        responses={200: sucsess_response, 401: unauthorized}
    )
    def post(self, request):
        serializer = TokenObtainSerializer(data=request.data)
        if serializer.is_valid():
            user = get_object_or_404(User, email=request.data['email'])
            otp_code = get_otp_code(user)
            to = [get_user_email(user)]
            tasks.send_otp_activation.delay(get_context(self.request, otp_code), to)
            return Response(self.sucsess_response, status=status.HTTP_200_OK)
        return Response(self.unauthorized, status=status.HTTP_401_UNAUTHORIZED)


class TokensObtainWithOtp(APIView):
    """Obtain a pair of JWT-tokens."""

    unauthorized = 'No account found with the given credentials'

    class Tokens:
        def __init__(self, refresh, access):
            self.refresh = refresh
            self.access = access

    @swagger_auto_schema(
        operation_description='Obtain a pair of JWT-tokens',
        request_body=OtpSerializer,
        responses={201: TokenRefreshSerializer, 401: unauthorized}
    )
    def post(self, request):
        serializer = OtpSerializer(data=request.data)
        if serializer.is_valid():
            user = get_object_or_404(User, email=request.data['email'])
            refresh = RefreshToken.for_user(user)
            tokens = self.Tokens(str(refresh), str(refresh.access_token))
            return Response(TokenRefreshSerializer(tokens).data, status=status.HTTP_201_CREATED)
