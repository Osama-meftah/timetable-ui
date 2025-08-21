from rest_framework import status
import pandas as pd
import io
from rest_framework.response import Response
from .models import *
from .serializers import *
import random
import string
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

def create_random_password():
    length = 8  # طول كلمة المرور
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password

def extract_username_from_email(email):
    if '@' in email:
        return email.split('@')[0]
    return email

def send_password_email(user, password):
    try:
        subject = "مرحبًا بك في نظام الجدول الزمني"
        from_email = settings.DEFAULT_FROM_EMAIL  # أو ضع بريدك مباشرة إذا لم تعرف
        recipient_list = [user.email]

        # رابط موقعك (عدّل الرابط ليكون رابط Host الفعلي)
        host_url = "https://timetable-frontend-mw47.onrender.com"
        # نص بديل (لمن لا يدعم HTML)
        text_content = (
            f"مرحبًا {user.get_full_name() or user.username},\n"
            f"تم إنشاء حسابك بنجاح.\n"
            f"اسم المستخدم: {user.username}\n"
            f"كلمة المرور: {password}\n"
            f"تفضل بتسجيل الدخول عبر الرابط: {host_url}\n"
            "شكرًا لانضمامك إلينا."
        )

        # نسخة HTML من الرسالة
        html_content = f"""
        <html lang="ar" dir="rtl">
        <body style="font-family: Tahoma, Arial, sans-serif; background-color: #f8f9fa; padding: 20px;">
            <div style="max-width: 500px; margin: auto; background-color: #ffffff; border-radius: 8px; padding: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                <h2 style="color: #4CAF50; text-align: center;">🎉 مرحبًا بك في ScheduleEase  🎉</h2>
                <p style="font-size: 16px; color: #333; text-align: center;">
                    عزيزي <strong>{user.get_full_name() or user.username}</strong>،
                    <br>
                    يسعدنا انضمامك إلى نظامنا. لقد تم إنشاء حسابك بنجاح.
                </p>
                <table style="width: 100%; margin-top: 20px; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 10px; background-color: #fafafa;">{user.username}</td>
                        <td style="padding: 10px; background-color: #f0f0f0; text-align: right;"> :اسم المستخدم</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; background-color: #fafafa;">{password}</td>
                        <td style="padding: 10px; background-color: #f0f0f0; text-align: right;"> :كلمة المرور</td>
                    </tr>
                </table>
                <div style="text-align: center; margin-top: 30px;">
                    <a href="{host_url}" style="background-color: #4CAF50; color: white; padding: 12px 20px; text-decoration: none; border-radius: 5px; font-size: 16px;">
                        🚀 تسجيل الدخول الآن
                    </a>
                </div>
            </div>
        </body>
        </html>
        """

        msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    except Exception as e:
        return Response({
            "status": "error",
            "message": "البريد الإلكتروني غير صالح",
            "details": f"{e}"
        })




def read_file_to_dataframe(file):
    file_content = io.BytesIO(file.read())
    if file.name.endswith('.csv'):
        return pd.read_csv(file_content)
    return pd.read_excel(file_content)


def validate_file(file):
    if not file:
        return False, "لم يتم إرسال أي ملف."
    if not file.name.endswith(('.csv', '.xls', '.xlsx')):
        return False, "صيغة الملف غير مدعومة. يرجى رفع ملف CSV أو Excel."
    return True, None
def is_field_valid(value):
        # print(value)
        # القيمة صالحة إذا كانت غير None وغير فارغة أو هي صفر (0 أو "0")
    return value is not None and (str(value).strip() != "" or str(value).strip() == "0")

def process_rows(df, required_fields, model_class, get_existing, prepare_data, serializer_class):
    success_count, fail_count, errors = 0, 0, []

    missing_columns = [col for col in required_fields if col not in df.columns]
    if missing_columns:
        return None, None, None, f"الملف ناقص الأعمدة التالية: {', '.join(missing_columns)}"

    df = df.fillna("").astype(str).apply(lambda x: x.str.strip())
    # print(df)

    for index, row in df.iterrows():
        try:
            # print(row)
            data = prepare_data(row)
            # print(data)
            if not all(is_field_valid(data.get(field)) for field in required_fields):
                errors.append(f"الصف {index + 2}: البيانات ناقصة.")
                fail_count += 1
                continue

            existing_instance = get_existing(data)
            if existing_instance:
                serializer = serializer_class(existing_instance, data=data, partial=True)
            else:
                serializer = serializer_class(data=data)

            if serializer.is_valid():
                serializer.save()
                success_count += 1
            else:
                errors.append(f"الصف {index + 2}: {serializer.errors}")
                fail_count += 1

        except Exception as e:
            errors.append(f"الصف {index + 2}: خطأ أثناء المعالجة: {str(e)}")
            fail_count += 1

    return success_count, fail_count, errors, None

def handle_upload(request, model, serializer_class, required_fields, get_existing, prepare_data, success_message_singular):
    file = request.FILES.get("data_file")
    is_valid, error = validate_file(file)
    if not is_valid:
        return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

    try:
        df = read_file_to_dataframe(file)
        success_count, fail_count, errors, missing = process_rows(
            df, required_fields, model, get_existing, prepare_data, serializer_class
        )
        
        if missing:
            return Response({"error": missing}, status=status.HTTP_400_BAD_REQUEST)

        if fail_count > 0:
            return Response({
                "message": f"✅ تم حفظ {success_count} {success_message_singular}. ❌ فشل في {fail_count} صف.",
                "errors": errors
            }, status=status.HTTP_207_MULTI_STATUS)

        return Response({"message": f"✅ تم إضافة/تحديث {success_count} {success_message_singular} بنجاح."}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": f"❌ حدث خطأ أثناء معالجة الملف: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def prepare_data_with_fk(row, fk_field, lookup_field, model, output_fk_field=None, display_name=None, extra_fields=None):
    extra_fields = extra_fields or []

    lookup_value = row.get(lookup_field)
    if not lookup_value:
        raise ValueError(f"⚠️ لم يتم العثور على قيمة لـ '{lookup_field}' في الصف.")

    related_instance = None
    if str(lookup_value).isdigit():
        related_instance = model.objects.filter(id=int(lookup_value)).first()
    if not related_instance:
        related_instance = model.objects.filter(name__iexact=str(lookup_value).strip()).first()

    if not related_instance:
        raise ValueError(f"⚠️ لم يتم العثور على {model.__name__} بالمعرف أو الاسم '{lookup_value}'.")

    data = {}

    for field in extra_fields:
        data[field] = row.get(field)

    if display_name:
        data[display_name] = row.get(display_name)

    output_fk_field = output_fk_field or fk_field
    data[output_fk_field] = related_instance.pk

    return data


def prepare_data_with_fk_name_to_id(row, fk_field, name_column, model, display_name=None, extra_fields=None):
    extra_fields = extra_fields or []

    name_value = row.get(name_column)
    if not name_value:
        raise ValueError(f"⚠️ العمود '{name_column}' فارغ.")

    # البحث عن الكائن المرتبط بالاسم
    related_instance = model.objects.filter(name__iexact=name_value.strip()).first()
    if not related_instance:
        raise ValueError(f"⚠️ لم يتم العثور على {model.__name__} بالاسم '{name_value}'.")

    data = {
        fk_field: related_instance.id
    }

    # إضافة الحقول الإضافية
    for field in extra_fields:
        data[field] = row.get(field)

    # display name = program_name مثلاً
    if display_name:
        data[display_name] = row.get(display_name)

    return data

# def get_existing_by_name_and_fk_name(data, model, name_field, fk_field):
#     return model.objects.filter(
#         **{
#             name_field: data.get(name_field),
#             fk_field: data.get(fk_field)
#         }
#     ).first()

# import re
# import random

# def generate_email(name):
#     normalized = re.sub(r'[^a-zA-Z0-9]+', '', name.lower())
#     normalized = normalized or "teacher"
#     suffix = random.randint(100, 999)
#     return f"{normalized}{suffix}@example.com"

# from django.core.validators import validate_email
# from django.core.exceptions import ValidationError

# def clean_email_or_generate(raw_email, fallback_name):
#     email = raw_email.strip()
#     try:
#         validate_email(email)
#         return email
#     except ValidationError:
#         return generate_email(fallback_name)

# def prepare_teacher_data(row):
#     name = row.get("teacher_name", "").strip()
#     if not name:
#         return {}

#     raw_email = row.get("teacher_email", "").strip()
#     email = clean_email_or_generate(raw_email, name)

#     return {
#         "teacher_name": name,
#         "teacher_email": email,
#         "teacher_phone": row.get("teacher_phone", "").strip(),
#         "teacher_address": row.get("teacher_address", "").strip(),
#         "teacher_status": row.get("teacher_status", "active").strip()
#     }
