from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import get_object_or_404
from django.utils import timezone
from djoser import signals
from djoser.compat import get_user_email
from djoser.views import UserViewSet
from drf_yasg.utils import swagger_auto_schema
from pyotp import random_base32, TOTP
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from templated_mail.mail import BaseEmailMessage
from users import tasks
from users.serializers import OtpSerializer


User = get_user_model()


class OtpUserViewSet(UserViewSet):
    def perform_create(self, serializer, *args, **kwargs):
        """Custom POST User method with sending email with OTP-code"""

        user = serializer.save(*args, **kwargs)
        signals.user_registered.send(sender=self.__class__, user=user, request=self.request)
        otp_code = self.get_otp_code(user)
        to = [get_user_email(user)]
        tasks.send_otp_activation.delay(self.get_context(self.request, otp_code), to)

    @staticmethod
    def get_otp_code(user):
        """Method for generating and saving the otp code and the time it was created"""

        otp_code = TOTP(random_base32(), digits=settings.OTP_LENTH).now()
        user.otp_code = make_password(otp_code)
        user.otp_created = timezone.now()
        user.save()
        return otp_code

    @staticmethod
    def get_context(request, otp_code):
        """Getting context for email template filling"""

        email = BaseEmailMessage(request)
        context = email.get_context_data()
        context.pop('view', None)
        context.pop('user', None)
        context.update({'otp_code': otp_code, 'template_name': settings.OTP_EMAIL_TEMPLATE})
        return context


class OtpActivateView(APIView):
    """User activation, only POST"""

    @swagger_auto_schema(
        operation_description='Set User is_active if OTP is valid',
        request_body=OtpSerializer,
        responses={200: OtpSerializer, 400: OtpSerializer}
    )
    def post(self, request):
        serializer = OtpSerializer(data=request.data)
        if serializer.is_valid():
            user = get_object_or_404(User, email=request.data['email'])
            otp_is_valid = check_password(request.data['otp_code'], user.otp_code)
            otp_expired = user.otp_created + settings.OTP_LIFETIME < timezone.now()
            if otp_is_valid and not otp_expired:
                user.is_active = True
                user.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
