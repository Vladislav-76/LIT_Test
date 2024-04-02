from celery import shared_task
from templated_mail.mail import BaseEmailMessage


class ActivationEmail(BaseEmailMessage):
    template_name = 'otp_activation.html'

    def get_context_data(self):
        # context = super().get_context_data()
        # user = context.get("user")
        # otp_code = TOTP(random_base32(), digits=settings.OTP_LENTH).now()
        # user.otp_code = make_password(otp_code)
        # user.otp_created = timezone.now()
        # user.save()
        # context['otp_code'] = otp_code
        return super().get_context_data()


@shared_task
def send_otp_activation(request, context, to):
    ActivationEmail(request, context).send(to)
