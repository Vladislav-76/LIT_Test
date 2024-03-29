from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(null=False, blank=False, unique=True)
    first_name = models.CharField(max_length=150, blank=True, verbose_name='First name')
    last_name = models.CharField(max_length=150, blank=True, verbose_name='Last name')
    is_verified = models.BooleanField(default=False, null=False, verbose_name='Verified by otp code')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    def __str__(self):
        return self.username

    class Meta:
        ordering = ("-id",)
        verbose_name = "User"
        verbose_name_plural = "Users"
