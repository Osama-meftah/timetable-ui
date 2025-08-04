import requests
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.core.cache import cache
BASE_API_URL = "http://127.0.0.1:8001/api/"

class Endpoints:
    login = "login/"
    logout = "logout/"
    user="user/"
    send_reseat_email="send_reseat_email/"
    send_forget_password_email="send_forget_password_email/"
    reseat_teacheer_password="reset-password/"
    departments = "departments/"
    departmentsUpload ="uploadDepartments/"
    programsUpload="uploadPrograms/"
    levelsUpload="uploadLevels/"
    todays: str = "todays/"
    periods = "periods/"
    halls = "halls/"
    uploadHalls = "uploadHalls/"
    tables = "tables/"
    programs = "programs/"
    levels = "levels/"
    groups = "groups/"
    teachers = "teachers/"
    teachersUpload = "teachersUpload/"
    teacher_times = "teacherTimes/"
    searchteacherstimes = "searchteacherstimes/"
    subjects = "subjects/"
    uploadSubjects = "uploadSubjects/"
    distributions = "distributions/"
    lectures = "lectures/by-table/"
    searchteachers = "searchteachers/"

class KeysCach:
    timeout=60
    teachers_data="teachers_data"
    teacher_times_data="teacher_times_data"
    distributions_data="distributions_data"
    days_data="days_data"
    periods_data="periods_data"
    group_data="group_data"
    subjects_data="subjects_data"

def get_or_cache(key, endpoint, request, timeout=KeysCach.timeout):
        data = cache.get(key)
        if data is None:
            data = api_get(endpoint, request=request) or []
            cache.set(key, data, timeout)
        return data

def show_backend_messages(request, response_json, default_success=""):
    if not request:
        return

    collected = {"success": [], "warning": [], "error": []}
    print(collected)
    def add(tag, msg):
        print(msg)
        if msg:
            collected[tag].append(msg)

    if isinstance(response_json, dict):
        add("success", response_json.get("message", default_success))

        for warning in response_json.get("warnings", []):
            add("warning", f"⚠️ {warning}")

        for error in response_json.get("errors", []):
            add("error", f"❌ {error}")

        if "detail" in response_json:
            add("error", f"❌ {response_json['detail']}")
    else:
        add("success", default_success)

    # إرسال الرسائل بعد التجميع
    for tag, msgs in collected.items():
        if msgs:
            combined = "\n".join(msgs)
            if tag == "success":
                messages.success(request, combined)
            elif tag == "warning":
                messages.warning(request, combined)
            elif tag == "error":
                messages.error(request, combined)

def handle_response(request, response):
    """
    يعالج الاستجابة القادمة من API ويعرض الرسائل المناسبة، ويعيد البيانات عند الحاجة.
    """
    if response is None:
        messages.error(request, "لم يتم الحصول على أي استجابة من الخادم")
        return "none", None

    if not isinstance(response, dict):
        messages.error(request, "تنسيق استجابة غير صالح")
        return "invalid", None

    status = response.get("status")
    message = response.get("message", "")
    data = response.get("data", None)

    if status == "success":
        return "success", data
    elif status == "error":
        if message:
            messages.error(request, message)
        return "error", None
    else:
        messages.warning(request, "تنسيق استجابة غير متوقع")
        return "unexpected", None


def show_backend_messages(request, response_json, default_success=""):
    if not request:
        return
    if isinstance(response_json, dict):
        if "message" in response_json:
            messages.success(request, response_json["message"])
        else:
            messages.success(request, default_success)

        if "warnings" in response_json and isinstance(response_json["warnings"], list):
            for warning in response_json["warnings"]:
                messages.warning(request, f"⚠️ {warning}")
        if "errors" in response_json and isinstance(response_json["errors"], list):
            for error in response_json["errors"]:
                messages.error(request, f"❌ {error}")
        if "detail" in response_json:
            messages.error(request, f"❌ {response_json['detail']}")
    else:
        messages.success(request, default_success)
        
def handle_exception(request, message, exception):
    full_message = f"{message}"
    if hasattr(exception, "response") and exception.response is not None:
        try:
            error_data = exception.response.json()
            if isinstance(error_data, dict):
                if "detail" in error_data:
                    full_message += f" - {error_data['detail']}"
                    if request:
                        messages.error(request, error_data["detail"])
                elif "message" in error_data:
                    full_message += f" - {error_data['message']}"
                    if request:
                        messages.error(request, error_data["message"])
                for key, val in error_data.items():
                    if key not in ["detail", "message"]:
                        if isinstance(val, list):
                            for item in val:
                                if request:
                                    messages.error(request, f"{key}: {item}")
                        else:
                            if request:
                                messages.error(request, f"{key}: {val}")
            else:
                if request:
                    messages.error(request, str(error_data))
        except Exception:
            if request:
                messages.error(request, str(exception))
    else:
        if request:
            messages.error(request, str(exception))
    return None

def api_get_with_token(endpoint,token):
    try:
        header={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
        }
        response = requests.get(f"{BASE_API_URL}{endpoint}", headers=header)
        # response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"POST request failed: {e}")


def api_get(endpoint, request=None, timeout=60, redirect_to=None, render_template=None, success_message=None, render_context=None):
    headers = {}
    if request and 'token' in request.session:
        headers["Authorization"] = f"Bearer {request.session['token']}"
    try:
        response = requests.get(f"{BASE_API_URL}{endpoint}", headers=headers, timeout=timeout)
        response.raise_for_status()
        try:
            data = response.json()
        except ValueError:
            msg = f"رد غير متوقع من الخادم: {response.text[:200]}"
            if request:
                messages.error(request, msg)
            if redirect_to:
                return redirect(redirect_to)
            return None

        show_backend_messages(request, data, success_message or "")

        if redirect_to:
            return redirect(redirect_to)

        if render_template:
            context = render_context or {}
            context.update({'data': data})
            return render(request, render_template, context)

        return data

    except requests.exceptions.Timeout:
        if request:
            messages.error(request, "⏳ انتهت مهلة الاتصال بالخادم.")
        if redirect_to:
            return redirect(redirect_to)
        if render_template:
            return render(request, render_template, render_context or {})
        return None

    except requests.exceptions.RequestException as e:
        handle_exception(request, "فشل في جلب البيانات", e)
        if redirect_to:
            return redirect(redirect_to)
        if render_template:
            return render(request, render_template, render_context or {})
        return None

def api_post(endpoint, data, request=None, success_message="", timeout=60, redirect_to=None, render_template=None, render_context=None):
    headers = {"Content-Type": "application/json"}
    if request and 'token' in request.session:
        headers["Authorization"] = f"Bearer {request.session['token']}"
    try:
        response = requests.post(f"{BASE_API_URL}{endpoint}", json=data, headers=headers, timeout=timeout)
        response.raise_for_status()
        try:
            data = response.json()

        except ValueError:
            msg = f"رد غير متوقع من الخادم: {response.text[:200]}"
            if request:
                messages.error(request, msg)
            if redirect_to:
                return redirect(redirect_to)
            if render_template:
                return render(request, render_template, render_context or {})
            return None

        show_backend_messages(request, data, success_message or "تم الاضافة بنجاح")

        if redirect_to:
            return redirect(redirect_to)

        if render_template:
            context = render_context or {}
            context.update({'data': data})
            return render(request, render_template, context)

        return data

    except requests.exceptions.Timeout:
        if request:
            messages.error(request, "⏳ انتهت مهلة الاتصال بالخادم.")
        if redirect_to:
            return redirect(redirect_to)
        if render_template:
            return render(request, render_template, render_context or {})
        return None

    except requests.exceptions.RequestException as e:
        handle_exception(request, "فشل في إرسال البيانات", e)
        if redirect_to:
            return redirect(redirect_to)
        if render_template:
            return render(request, render_template, render_context or {})
        return None

def api_put(endpoint, data, request=None, timeout=60, redirect_to=None, render_template=None, render_context=None):
    headers = {"Content-Type": "application/json"}
    if request and 'token' in request.session:
        headers["Authorization"] = f"Bearer {request.session['token']}"
    try:
        response = requests.put(f"{BASE_API_URL}{endpoint}", json=data, headers=headers, timeout=timeout)
        response.raise_for_status()
        try:
            data = response.json()
        except ValueError:
            msg = f"رد غير متوقع من الخادم: {response.text[:200]}"
            if request:
                messages.error(request, msg)
            if redirect_to:
                return redirect(redirect_to)
            if render_template:
                return render(request, render_template, render_context or {})
            return None

        show_backend_messages(request, data)

        if redirect_to:
            return redirect(redirect_to)

        if render_template:
            context = render_context or {}
            context.update({'data': data})
            return render(request, render_template, context)

        return data

    except requests.exceptions.Timeout:
        if request:
            messages.error(request, "⏳ انتهت مهلة الاتصال بالخادم.")
        if redirect_to:
            return redirect(redirect_to)
        if render_template:
            return render(request, render_template, render_context or {})
        return None

    except requests.exceptions.RequestException as e:
        handle_exception(request, "فشل في تعديل البيانات", e)
        if redirect_to:
            return redirect(redirect_to)
        if render_template:
            return render(request, render_template, render_context or {})
        return None

def api_delete(endpoint, request=None, timeout=60, redirect_to=None, render_template=None, render_context=None):
    headers = {}
    if request and 'token' in request.session:
        headers["Authorization"] = f"Bearer {request.session['token']}"
    try:
        response = requests.delete(f"{BASE_API_URL}{endpoint}", headers=headers, timeout=timeout)
        response.raise_for_status()
        if request:
            messages.success(request, "✅ تم الحذف بنجاح")
        if redirect_to:
            return redirect(redirect_to)
        if render_template:
            return render(request, render_template, render_context or {})
        return True
    except requests.exceptions.Timeout:
        if request:
            messages.error(request, "⏳ انتهت مهلة الاتصال بالخادم.")
        if redirect_to:
            return redirect(redirect_to)
        if render_template:
            return render(request, render_template, render_context or {})
        return False
    except requests.exceptions.RequestException as e:
        handle_exception(request, "فشل في حذف العنصر", e)
        if redirect_to:
            return redirect(redirect_to)
        if render_template:
            return render(request, render_template, render_context or {})
        return False
    
def api_search_items(endpoint, query, request):
    """
    إرسال طلب GET إلى API يحتوي على فلترة بالبحث، مع التوكن ومعالجة الأخطاء.
    """
    url = f"{BASE_API_URL}{endpoint}?q={query}"
    print(url)
    token = request.session.get("token")

    headers = {
        "Content-Type": "application/json"
    }
    if token:
        headers["Authorization"] = f"Token {token}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        # print(response)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and 'results' in data:
            return data['results']
        else:
            return []

    except requests.exceptions.RequestException as e:
        # طباعة الخطأ لغايات التصحيح فقط (أزلها لاحقًا في الإنتاج)
        print("API search error:", e)
        return []

def handle_file_upload_generic(request, *, file_field_name, endpoint_url, success_title="✅ تم رفع الملف", error_title="❌ خطأ في رفع الملف", timeout=20, redirect_to=None, render_template=None, render_context=None):
    file = request.FILES.get(file_field_name)
    if not file:
        messages.error(request, "يرجى اختيار ملف.")
        if redirect_to:
            return redirect(redirect_to)
        if render_template:
            return render(request, render_template, render_context or {})
        return

    allowed_types = [
        "text/csv",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ]
    if file.content_type not in allowed_types:
        messages.error(request, "صيغة الملف غير مدعومة.")
        if redirect_to:
            return redirect(redirect_to)
        if render_template:
            return render(request, render_template, render_context or {})
        return

    try:
        files = {
            'data_file': (file.name, file.read(), file.content_type)
        }

        response = requests.post(endpoint_url, files=files, timeout=timeout)
        response.raise_for_status()

        try:
            response_data = response.json()
            show_backend_messages(request, response_data, success_title)

        except ValueError:
            messages.success(request, f"{success_title}. (الرد: {response.text})")

        if redirect_to:
            return redirect(redirect_to)

        if render_template:
            return render(request, render_template, render_context or {})

    except requests.exceptions.Timeout:
        messages.error(request, "⏳ انتهت مهلة الاتصال بالخادم.")
        if redirect_to:
            return redirect(redirect_to)
        if render_template:
            return render(request, render_template, render_context or {})
    except requests.exceptions.RequestException as e:
        handle_exception(request, error_title, e)
        if redirect_to:
            return redirect(redirect_to)
        if render_template:
            return render(request, render_template, render_context or {})

def handle_file_upload(request, file_field_name, endpoint_url, success_title, error_title, redirect_to):
    try:
        return handle_file_upload_generic(
            request,
            file_field_name=file_field_name,
            endpoint_url=endpoint_url,
            success_title=success_title,
            error_title=error_title,
            redirect_to=redirect_to
        )
    except Exception as e:
        messages.error(request, f"{error_title}: {e}")
        return redirect(redirect_to)

def paginate_queryset(queryset, request, page_key, page_size_key, size=5):
    try:
        page_number = request.GET.get(page_key, 1)
        page_size = int(request.GET.get(page_size_key, size))
        paginator = Paginator(queryset, page_size)
        return paginator.get_page(page_number)
    except Exception as e:
        if hasattr(request, "session"):
            messages.error(request, f"خطأ في التحويل للصفحات: {e}")
        return queryset

# def fetch_paginated_api_data(api_url, request, page_param="page", page_size_param="page_size", default_page_size=10, cache_timeout=60):
#     """
#     دالة عامة لجلب بيانات paginated من API يدعم pagination في الـ backend مع استخدام cache.
#     """
#     page = request.GET.get(page_param, 1)
#     page_size = request.GET.get(page_size_param, default_page_size)
    
#     try:
#         page = int(page)
#     except (ValueError, TypeError):
#         page = 1

#     try:
#         page_size = int(page_size)
#     except (ValueError, TypeError):
#         page_size = default_page_size

#     # إنشاء مفتاح للكاش بناءً على الرابط والمعاملات
#     cache_key = f"api_cache:{api_url}:page={page}:page_size={page_size}"

#     # محاولة الحصول من الكاش
#     cached_data = cache.get(cache_key)
#     if cached_data is not None:
#         return cached_data

#     params = {
#         page_param: page,
#         page_size_param: page_size,
#     }

#     try:
#         response = requests.get(api_url, params=params)
#         response.raise_for_status()
#         data = response.json()
#     except Exception:
#         # في حالة الخطأ، رجع بيانات فارغة أو من الكاش القديم لو تبي
#         return {
#             "results": [],
#             "count": 0,
#             "next_url": None,
#             "prev_url": None,
#             "current_page": page,
#             "total_pages": 1,
#             "page_size": page_size,
#         }

#     count = data.get("count", 0)
#     results = data.get("results", [])
#     next_url = data.get("next")
#     prev_url = data.get("previous")
#     total_pages = (count + page_size - 1) // page_size if page_size else 1

#     result_data = {
#         "results": results,
#         "count": count,
#         "next_url": next_url,
#         "prev_url": prev_url,
#         "current_page": page,
#         "total_pages": total_pages,
#         "page_size": page_size,
#     }
#     # حفظ البيانات في الكاش
#     cache.set(cache_key, result_data, cache_timeout)  # timeout بالثواني

#     return result_data

def get_user_id(request):
    """
    استرجاع معرف المستخدم من الجلسة.
    """
    user =request.session.get('user')
    # print(user)
    # user_id = user.get('id') if user else None

    return user
