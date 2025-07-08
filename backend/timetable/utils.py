from rest_framework import status
import pandas as pd
import io
from rest_framework.response import Response
from .models import *
from .serializers import *
import re
import random


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
    print(df)

    for index, row in df.iterrows():
        try:
            print(row)
            data = prepare_data(row)
            print(data)
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

def prepare_data_with_fk(row, fk_field, lookup_field, model, display_name=None, extra_fields=None):
    extra_fields = extra_fields or []

    # جلب قيمة المفتاح الأجنبي من الصف
    lookup_value = row.get(lookup_field)

    # محاولة جلب الكائن المرتبط بالمفتاح (أو الاسم لو لم يكن رقمياً)
    related_instance = None
    if lookup_value:
        if str(lookup_value).isdigit():
            related_instance = model.objects.filter(id=int(lookup_value)).first()
        if not related_instance:
            related_instance = model.objects.filter(name=str(lookup_value).strip()).first()

    if not related_instance:
        raise ValueError(f"⚠️ {display_name or fk_field}: لم يتم العثور على {model.__name__} بالمعرف أو الاسم '{lookup_value}'.")

    data = {}

    # جلب باقي الحقول الإضافية
    for field in extra_fields:
        data[field] = row.get(field)

    # إضافة display_name لو معرف
    if display_name:
        data[display_name] = row.get(display_name)

    # ✅ إضافة المفتاح الأصلي للتأكد من اكتمال البيانات
    data[lookup_field] = lookup_value

    # ✅ إضافة المفتاح الأجنبي الفعلي
    data[fk_field] = related_instance.pk

    return data

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
#         "teacher_status": row.get("teacher_status", "نشط").strip()
#     }
