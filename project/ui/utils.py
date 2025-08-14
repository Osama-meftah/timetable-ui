import requests
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.core.cache import cache
from urllib.parse import urlparse, parse_qs
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
    refreshToken ='token/refresh/'

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
    def add(tag, msg):
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
                    # if key=="status":
                    #     continue
                    if key not in ["detail", "message","error"]:

                        if isinstance(val, list):
                            for item in val:
                                print(f"items {item} {val}")
                                if request:
                                    messages.error(request, f"{item} {val} ")
                        else:
                            if request:
                                messages.error(request, f"{val}")
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
 
def _refresh_and_save_tokens(request):
    """Attempts to refresh the access token. Returns True on success, False on failure."""
    refresh_token = request.session.get('refresh_token')
    if not refresh_token:
        return False

    try:
        response = requests.post(f"{BASE_API_URL}{Endpoints.refreshToken}", json={'refresh': refresh_token}, timeout=10)
        response.raise_for_status()
        new_tokens = response.json()
        request.session['token'] = new_tokens['access']
        if 'refresh' in new_tokens:
            request.session['refresh_token'] = new_tokens['refresh']
        return True
    except requests.RequestException:
        return False


def logout_view(request):
        request.session.flush()  # Clear the session
        messages.success(request, "Logged out successfully!")
        return redirect('login')  # Redirect to the login page



def _api_request(method, endpoint, request, is_retry=False, **kwargs):

    headers = kwargs.get("headers", {})
    if 'Content-Type' not in headers and 'files' not in kwargs:
        headers['Content-Type'] = 'application/json'

    if request and 'token' in request.session:
        headers["Authorization"] = f"Bearer {request.session['token']}"
    
    kwargs["headers"] = headers
    
    try:
        response = requests.request(method, f"{BASE_API_URL}{endpoint}", **kwargs)
        response.raise_for_status()
        if response.status_code == 204:
            return True
        return response.json()

    except requests.exceptions.RequestException as e:
        if not is_retry and e.response and e.response.status_code == 401:
            if _refresh_and_save_tokens(request):
                return _api_request(method, endpoint, request, is_retry=True, **kwargs)
            else:
                return "LOGOUT" # Signal that refresh failed
        
        handle_exception(request, f"فشل الطلب من نوع {method.upper()}", e)
        return None


def _handle_api_response(request, response, redirect_to=None, render_template=None, render_context=None, success_message=None):
    """
    Processes the result from _api_request and performs Django-specific actions
    like redirecting, rendering, or simply returning the data.
    """
    # Case 1: Critical auth failure, requires immediate logout
    # if response == "LOGOUT":
    #     return logout_view(request)

    # Case 2: The request failed for other reasons (e.g., network error, 500 server error)
    if response is None:
        if redirect_to:
            return redirect(redirect_to)
        if render_template:
            return render(request, render_template, render_context or {})
        return None # Return None to the view

    # Case 3: The request was successful
    # Display success messages
    if isinstance(response, dict):
        show_backend_messages(request, response, default_success=success_message or "")
    elif success_message:
        messages.success(request, success_message)

    # Perform action based on parameters
    if redirect_to:
        return redirect(redirect_to)
    
    if render_template:
        context = render_context or {}
        context['data'] = response # Add the API data to the context
        return render(request, render_template, context)
        
    return response # Default action: return the raw response to the view

# ================================================================= #
#                PUBLIC API WRAPPERS (Your Interface)               #
# ================================================================= #

def api_get(endpoint, request=None, timeout=60, redirect_to=None, render_template=None, success_message=None, render_context=None):
    raw_response = _api_request("get", endpoint, request, timeout=timeout)
    return _handle_api_response(request, raw_response, redirect_to, render_template, render_context, success_message)

def api_post(endpoint, data, request=None, timeout=60, redirect_to=None, render_template=None, success_message=None, render_context=None):
    raw_response = _api_request("post", endpoint, request, timeout=timeout, json=data)
    return _handle_api_response(request, raw_response, redirect_to, render_template, render_context, success_message)

def api_put(endpoint, data, request=None, timeout=60, redirect_to=None, render_template=None, success_message=None, render_context=None):
    raw_response = _api_request("put", endpoint, request, timeout=timeout, json=data)
    return _handle_api_response(request, raw_response, redirect_to, render_template, render_context, success_message)

def api_delete(endpoint, request=None, timeout=60, redirect_to=None, render_template=None, success_message=None, render_context=None):
    raw_response = _api_request("delete", endpoint, request, timeout=timeout)
    # Use a more specific success message for delete if not provided
    final_success_message = success_message or "تم الحذف بنجاح"
    return _handle_api_response(request, raw_response, redirect_to, render_template, render_context, final_success_message)


def api_search_items(endpoint, query, request):
    """
    إرسال طلب GET إلى API يحتوي على فلترة بالبحث، مع التوكن ومعالجة الأخطاء.
    """
    url = f"{BASE_API_URL}{endpoint}?q={query}"
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



def get_data_details(data):
    links = data.get("links", {})
    return (
        data.get("results", []),
        data.get("count", 0),
        data.get("total_pages", 0),
        links.get("next"),
        links.get("previous"),
        data.get("current_page", 1)  # ✅ استخراج رقم الصفحة الحالية
    )
def get_current_page(url):
    if not url:
        return 1
    query = parse_qs(urlparse(url).query)
    # هذا هو السطر السحري
    return int(query.get("page", [1])[0]) 


def get_user_id(request):
    return request.session.get('user')
