from celery import shared_task
from templated_mail.mail import BaseEmailMessage


@shared_task
def send_otp_activation(context, to):
    """Celery task for email sendig"""

    email = BaseEmailMessage(context=context)
    email.template_name = context['template_name']
    email.send(to)
