# _*_ coding: utf-8 _*_

# _Author_: 'Anson'

# _Time_: '2019-06-05 16:33'

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def create_user(sender, instance=None, created=False, **kwargs):
    print('来啦')
    if created:
        password = instance.password
        instance.set_password(password)
        instance.save()