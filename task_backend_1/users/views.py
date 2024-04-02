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
# from templated_mail.mail import BaseEmailMessage
from users import tasks
from users.serializers import OtpSerializer


User = get_user_model()


# class ActivationEmail(BaseEmailMessage):
#     template_name = 'otp_activation.html'

#     def get_context_data(self):
#         # context = super().get_context_data()
#         # user = context.get("user")
#         # otp_code = TOTP(random_base32(), digits=settings.OTP_LENTH).now()
#         # user.otp_code = make_password(otp_code)
#         # user.otp_created = timezone.now()
#         # user.save()
#         # context['otp_code'] = otp_code
#         return super().get_context_data()


class OtpUserViewSet(UserViewSet):
    def perform_create(self, serializer, *args, **kwargs):
        user = serializer.save(*args, **kwargs)
        signals.user_registered.send(sender=self.__class__, user=user, request=self.request)
        otp_code = self.get_otp_code(user)
        context = {'user': user, 'otp_code': otp_code}
        to = [get_user_email(user)]
        tasks.send_otp_activation.delay(self.request, context, to)
        # ActivationEmail(self.request, context).send(to)

    @staticmethod
    def get_otp_code(user):
        otp_code = TOTP(random_base32(), digits=settings.OTP_LENTH).now()
        user.otp_code = make_password(otp_code)
        user.otp_created = timezone.now()
        user.save()
        return otp_code


class OtpActivateView(APIView):
    @swagger_auto_schema(
        operation_description='Set User is_active if OTP is valid',
        request_body=OtpSerializer,
        responses={200: OtpSerializer, 400: OtpSerializer}
    )
    def post(self, request):
        serializer = OtpSerializer(data=request.data)
        if serializer.is_valid():
            user = get_object_or_404(User, id=request.data['user_id'])
            otp_is_valid = check_password(request.data['otp_code'], user.otp_code)
            otp_expired = user.otp_created + settings.OTP_LIFETIME < timezone.now()
            if otp_is_valid and not otp_expired:
                user.is_active = True
                user.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
