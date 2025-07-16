from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Teacher

# @receiver(post_save, sender=Teacher)
# def create_teacher_profile(sender,instance,created,**kwargs):
#     if created:
#         # إنشاء ملف تعريف المعلم عند إنشاء مستخدم جديد
#         user=
        
#         # إرسال بريد إلكتروني للترحيب بالمعلم الجديد
#         # send_mail(
#         #     'Welcome to the Timetable System',
#         #     'Your account has been created successfully.',            '
