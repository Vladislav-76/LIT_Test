from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken


from users import views

User = get_user_model()


class OtpCode(serializers.Field):
    """Custom serializer field class."""

    def to_internal_value(self, value):
        if not value.isnumeric():
            raise serializers.ValidationError('All characters must be digits')
        if len(value) != settings.OTP_LENTH:
            raise serializers.ValidationError(f'Code length must be {settings.OTP_LENTH} digits')
        return value

    def to_representation(self, value):
        return value


class OtpSerializer(serializers.Serializer):
    """OTP-code obtain serializer."""

    email = serializers.EmailField()
    otp_code = OtpCode()

    default_error_messages = {'invalid_credentials': 'No account found with the given credentials'}

    def validate(self, attrs):
        user = get_object_or_404(User, email=attrs['email'])
        if views.users_otp.get(user.id, None):
            otp_is_valid = attrs['otp_code'] == views.users_otp[user.id]['otp_code']
            otp_expired = views.users_otp[user.id]['otp_created'] + settings.OTP_LIFETIME < timezone.now()
        else:
            otp_is_valid = False
        if not otp_is_valid or otp_expired:
            raise AuthenticationFailed(self.error_messages['invalid_credentials'])
        return attrs
