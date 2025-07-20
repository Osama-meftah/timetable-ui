import requests
from django.contrib import messages
from types import SimpleNamespace
from django.core.paginator import Paginator
BASE_API_URL = "http://127.0.0.1:8001/api/"

class Endpoints:
    login = "login/"
    logout = "logout/"
    user="user/"
    send_reseat_email="send_reseat_email"
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
    subjects = "subjects/"
    uploadSubjects = "uploadSubjects/"
    distributions = "distributions/"
    lectures = "lectures/"


def handle_response(request, response):
    """
    يعالج الاستجابة القادمة من API ويعرض الرسائل المناسبة، ويعيد البيانات عند الحاجة.
    """
    status = response.get("status")
    message = response.get("message", "")
    data = response.get("data", None)  # يمكن أن تكون None إذا لم توجد بيانات

    if status == "success":
        if message:
            messages.success(request, message)
        return True, data  # success, مع البيانات
    elif status == "error":
        if message:
            messages.error(request, message)
        return False, None  # فشل، لا يوجد بيانات
    else:
        messages.warning(request, "تنسيق استجابه غير متوقع")
        return False, None

def api_get(endpoint):
    try:
        
        response = requests.get(f"{BASE_API_URL}{endpoint}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"GET request failed: {e}")

def api_post(endpoint, data):
    try:
        print(f"{BASE_API_URL}{endpoint}", data)
        response = requests.post(f"{BASE_API_URL}{endpoint}", json=data)
        # response.raise_for_status()

        return response.json()
    
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"POST request failed: {e}")

def api_get_with_token(endpoint,token):
    try:
        header={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
        }
        response = requests.get(f"{BASE_API_URL}{endpoint}", headers=header)
        response.raise_for_status()

        return response.json()
    
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"POST request failed: {e}")

def api_put(endpoint, data):
    try:
        response = requests.put(f"{BASE_API_URL}{endpoint}", json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"PUT request failed: {e}")

def api_delete(endpoint):
    try:
        response = requests.delete(f"{BASE_API_URL}{endpoint}")
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"DELETE request failed: {e}")

def handle_exception(request, message, exception):
    error_message = f"{message}: {exception}"
    try:
        error_details = exception.response.json()
        error_message += f" التفاصيل: {error_details}"
    except:
        pass
    messages.error(request, error_message)
    return error_message



def handle_file_upload_generic(request, *, file_field_name, endpoint_url, success_title="✅ تم رفع الملف", error_title="❌ خطأ في رفع الملف"):
    file = request.FILES.get(file_field_name)
    if not file:
        messages.error(request, "يرجى اختيار ملف.")
        return

    allowed_types = [
        "text/csv",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ]
    if file.content_type not in allowed_types:
        messages.error(request, "صيغة الملف غير مدعومة.")
        return

    try:
        files = {
            'data_file': (file.name, file.read(), file.content_type)
        }

        response = requests.post(endpoint_url, files=files, timeout=20)
        response.raise_for_status()

        try:
            response_data = response.json()
            msg = response_data.get("message", success_title)
            messages.success(request, msg)

            errors = response_data.get("errors")
            if errors:
                for error in errors:
                    messages.warning(request, f"⚠️ {error}")

        except ValueError:
            # الرد ليس JSON
            messages.success(request, f"{success_title}. (الرد: {response.text})")

    except requests.exceptions.Timeout:
        messages.error(request, "⏳ انتهت مهلة الاتصال بالخادم.")
    except requests.exceptions.RequestException as e:
        messages.error(request, f"{error_title}: {e}")

def paginate_queryset(queryset, request, page_key="page", page_size_key="page_size",size=5):
    page_number = request.GET.get(page_key, 1)
    page_size = request.GET.get(page_size_key, size)
    paginator = Paginator(queryset, page_size)
    return paginator.get_page(page_number)
