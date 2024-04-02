from django.conf import settings
from rest_framework import serializers


class OtpCode(serializers.Field):
    """Custom serializer field class"""

    def to_internal_value(self, value):
        if not value.isnumeric():
            raise serializers.ValidationError('All characters must be digits')
        if len(value) != settings.OTP_LENTH:
            raise serializers.ValidationError(f'Code length must be {settings.OTP_LENTH} digits')
        return value

    def to_representation(self, value):
        return value


class OtpSerializer(serializers.Serializer):
    """OTP-code obtain serializer"""

    email = serializers.EmailField()
    otp_code = OtpCode()
