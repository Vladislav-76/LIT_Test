from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(null=False, blank=False, unique=True)
    first_name = models.CharField(max_length=150, blank=True, verbose_name='First name')
    last_name = models.CharField(max_length=150, blank=True, verbose_name='Last name')
    otp_code = models.CharField(max_length=100, blank=True, null=True, verbose_name='OTP-code')
    otp_created = models.DateTimeField(blank=True, null=True, verbose_name='OTP creation time')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    def __str__(self):
        return self.username

    class Meta:
        ordering = ("-id",)
        verbose_name = "User"
        verbose_name_plural = "Users"
