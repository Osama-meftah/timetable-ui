from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
import requests
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .utlis import api_delete,api_get,api_post,api_put,handle_exception
from django.middleware.csrf import get_token



BASE_API_URL = "http://127.0.0.1:8001/api/"

def login(request):
    """
    عرض صفحة تسجيل الدخول.
    """
    return render(request, 'login.html')

def dashboard(request):
    """
    عرض لوحة التحكم.
    """
    return render(request, 'dashboard.html')


class TeachersView(View):
    def get(self, request):
        try:
            teachers_data = api_get("teachers/")
            teacher_times_data = api_get("teacherTimes/")
            distributions_data = api_get("distributions/")

            teachers_with_data = []
            for teacher in teachers_data:
                teacher_id = teacher["id"]
                courses = [
                    {
                        "subject_name": d["fk_subject"]["subject_name"],
                        "group": d["fk_group"]["group_name"],
                        "level": d["fk_group"]["fk_level"]["level_name"],
                        "program": d["fk_group"]["fk_level"]["fk_program"]["program_name"],
                    }
                    for d in distributions_data
                    if d["fk_teacher"]["id"] == teacher_id
                ]
                times = [
                    {
                        "day": t["fk_today"]["day_name_display"],
                        "period": t["fk_period"]["period_display"]
                    }
                    for t in teacher_times_data
                    if t["fk_teacher"]["id"] == teacher_id
                ]

                if courses:  # فقط المدرسين الذين لديهم توزيع
                    teachers_with_data.append({
                        "teacher": teacher,
                        "courses": courses,
                        "availability": times,
                    })

            total_teachers = len(teachers_data)
            active_teachers = len([t for t in teachers_data if t.get("teacher_status") == "نشط"])
            on_leave_teachers = len([t for t in teachers_data if t.get("teacher_status") == "إجازة"])

            # إعداد Pagination
            page_teachers = request.GET.get("page", 1)
            page_teachers_size = request.GET.get("page_size", 10)
            page_teachers_data_size = request.GET.get("page_data_size", 10)

            paginator_teachers = Paginator(teachers_data, page_teachers_size)
            paginator_detailed = Paginator(teachers_with_data, page_teachers_data_size)

            try:
                teachers_paginated = paginator_teachers.page(page_teachers)
                teachers_data_paginated = paginator_detailed.page(page_teachers)
            except PageNotAnInteger:
                teachers_paginated = paginator_teachers.page(1)
                teachers_data_paginated = paginator_detailed.page(1)
            except EmptyPage:
                teachers_paginated = paginator_teachers.page(paginator_teachers.num_pages)
                teachers_data_paginated = paginator_detailed.page(paginator_detailed.num_pages)

            context = {
                "page_title": "إدارة المدرسين",
                "teachers": teachers_paginated,
                "teachers_with_data": teachers_data_paginated,
                "total_teachers": total_teachers,
                "active_teachers": active_teachers,
                "on_leave_teachers": on_leave_teachers,
            }
            return render(request, "teachers/list.html", context)

        except Exception as e:
            handle_exception(request, "فشل في جلب بيانات المدرسين", e)
            return render(request, "teachers/list.html", {
                "teachers": [],
                "teachers_with_data": [],
                "error": "فشل في جلب بيانات المدرسين."
            })

class TeacherFormView(View):
    def get(self, request, id=None):
        teacher = None
        if id:
            try:
                teacher = api_get(f"teachers/{id}/")
            except Exception as e:
                handle_exception(request, "فشل في جلب بيانات المدرس", e)
                return redirect("teachers_management")
        return render(request, "teachers/add_edit.html", {"teacher": teacher})

    def post(self, request, id=None):
        teacher_data = {
            "id": id,
            "teacher_name": request.POST.get("teacher_name", "").strip(),
            "teacher_phone": request.POST.get("teacher_phone", "").strip(),
            "teacher_email": request.POST.get("teacher_email", "").strip(),
            "teacher_address": request.POST.get("teacher_address", "").strip(),
            "teacher_status": request.POST.get("teacher_status", "").strip(),
        }

        if not teacher_data["teacher_name"] or not teacher_data["teacher_email"]:
            messages.error(request, "الاسم والبريد الإلكتروني مطلوبان.")
            return redirect("teachers_management")

        try:
            if id:
                api_put(f"teachers/{id}/", teacher_data)
                messages.success(request, "تم تعديل بيانات المدرس بنجاح.")
            else:
                api_post("teachers/", teacher_data)
                messages.success(request, "تم إضافة المدرس بنجاح.")
        except Exception as e:
            handle_exception(request, "حدث خطأ أثناء حفظ بيانات المدرس", e)

        return redirect("teachers_management")
    
class TeacherDeleteView(View):
    def post(self, request, id):
        try:
            api_delete(f"teachers/{id}/")
            messages.success(request, "تم حذف المدرس بنجاح.")
        except Exception as e:
            handle_exception(request, "حدث خطأ أثناء حذف المدرس", e)
        return redirect("teachers_management")


class TeacherAvailabilityAndCoursesView(View):
    endpoints = {
        "teachers": "teachers/",
        "teacher_times": "teacherTimes/",
        "distributions": "distributions/",
        "todays": "todays/",
        "periods": "periods/",
        "subjects": "subjects/",
        "groups": "groups/",
        "levels": "levels/",
        "programs": "programs/",
    }

    def get(self, request, id=None):
        try:
            teachers = requests.get(f"{BASE_API_URL}{self.endpoints['teachers']}").json()
            days = requests.get(f"{BASE_API_URL}{self.endpoints['todays']}").json()
            periods = requests.get(f"{BASE_API_URL}{self.endpoints['periods']}").json()
            subjects = requests.get(f"{BASE_API_URL}{self.endpoints['subjects']}").json()
            levels = requests.get(f"{BASE_API_URL}{self.endpoints['levels']}").json()
            programs = requests.get(f"{BASE_API_URL}{self.endpoints['programs']}").json()
            groups = requests.get(f"{BASE_API_URL}{self.endpoints['groups']}").json()

            # البيانات الخاصة بالمدرس إن وجد
            teacher = None
            teacher_times = []
            teacher_distributions = []
            if id:
                teacher = requests.get(f"{BASE_API_URL}{self.endpoints['teachers']}{id}/").json()

                all_times = requests.get(f"{BASE_API_URL}{self.endpoints['teacher_times']}").json()
                teacher_times = [t for t in all_times if t["fk_teacher"]["id"] == int(id)]

                all_distributions = requests.get(f"{BASE_API_URL}{self.endpoints['distributions']}").json()
                teacher_distributions = [d for d in all_distributions if d["fk_teacher"]["id"] == int(id)]

            context = {
                "teacher": teacher,
                "all_teachers": teachers,
                "teacher_times": teacher_times,
                "teacher_distributions": teacher_distributions,
                "days": days,
                "periods": periods,
                "subjects": subjects,
                "levels": levels,
                "programs": programs,
                "groups": groups,
                "page_title": "تعديل" if id else "إضافة",
            }
            return render(request, "teachers/add_edit_teacher_with_courses.html", context)

        except requests.exceptions.RequestException as e:
            messages.error(request, f"فشل في جلب البيانات: {e}")
            return redirect("teachers_management")
    def post(self, request, id=None):
            form_type = request.POST.get('form_type')
            teacher_id = request.POST.get('selected_teacher_id')

            if not teacher_id:
                messages.error(request, "يرجى اختيار المدرس.")
                return redirect(request.path_info)

            try:
                if form_type == "courses_form":
                    for i in range(1, 100):
                        group_id = request.POST.get(f'dist_group_{i}')
                        subject_id = request.POST.get(f'dist_subject_{i}')
                        dist_id = request.POST.get(f'distribution_id_{i}')
                        dist_id_add = request.POST.get(f'distribution_id_{i}_add')

                        if group_id and subject_id:
                            dist_data = {
                                "fk_group_id": group_id,
                                "fk_teacher_id": teacher_id,
                                "fk_subject_id": subject_id,
                            }

                            try:
                                if dist_id_add:
                                    api_post(self.endpoints["distributions"], dist_data) 
                                    print("add")
                                elif dist_id:
                                    api_put(f"{self.endpoints['distributions']}{dist_id}/", dist_data)
                                else:
                                    print("add+")
                                    api_post(self.endpoints["distributions"], dist_data)
                            except Exception as e:
                                handle_exception(request, f"فشل حفظ توزيع رقم {i}", e)
                        else:
                            break

                    messages.success(request, "تم حفظ المقررات بنجاح.")

                elif form_type == "times_form":
                    for i in range(1, 100):
                        day_id = request.POST.get(f'time_day_{i}')
                        period_id = request.POST.get(f'time_period_{i}')
                        availability_id = request.POST.get(f'availability_id_{i}')
                        availability_id_add = request.POST.get(f'availability_id_{i}_add')

                        if day_id and period_id:
                            time_data = {
                                "fk_today_id": day_id,
                                "fk_period_id": period_id,
                                "fk_teacher_id": teacher_id,
                            }
                            
                            try:
                                if availability_id_add:
                                    print(availability_id_add)
                                    print(day_id)
                                    print("add")
                                    api_post(self.endpoints["teacher_times"], time_data)
                                elif availability_id:
                                    print(availability_id_add)
                                    print(day_id)
                                    print("edit")
                                    api_put(f"{self.endpoints['teacher_times']}{availability_id}/", time_data)
                                else:
                                    print("add+")
                                    api_post(self.endpoints["teacher_times"], time_data)
                            except Exception as e:
                                handle_exception(request, f"فشل حفظ وقت رقم {i}", e)
                        else:
                            break

                    messages.success(request, "تم حفظ الأوقات المتاحة بنجاح.")

                elif form_type == "delete_distribution":
                    dist_id = request.POST.get("distribution_id")
                    if dist_id:
                        try:
                            api_delete(f"{self.endpoints['distributions']}{dist_id}/")
                            messages.success(request, "تم حذف توزيع المقرر بنجاح.")
                        except Exception as e:
                            handle_exception(request, "فشل في حذف توزيع المقرر", e)

                elif form_type == "delete_availability":
                    availability_id = request.POST.get("availability_id")
                    if availability_id:
                        try:
                            api_delete(f"{self.endpoints['teacher_times']}{availability_id}/")
                            messages.success(request, "تم حذف وقت التوفر بنجاح.")
                        except Exception as e:
                            handle_exception(request, "فشل في حذف وقت التوفر", e)

                else:
                    messages.error(request, "نوع النموذج غير معروف.")

                return redirect("add_edit_teacher_with_courses", id=teacher_id)

            except Exception as e:
                handle_exception(request, "حدث خطأ أثناء الحفظ", e)
                return redirect(request.path_info)

    # def post(self, request, id=None):
    #     form_type = request.POST.get('form_type')
    #     teacher_id = request.POST.get('selected_teacher_id')

    #     if not teacher_id:
    #         messages.error(request, "يرجى اختيار المدرس.")
    #         return redirect(request.path_info)

    #     try:
    #         if form_type == "courses_form":
    #             for i in range(1, 100):
    #                 group_id = request.POST.get(f'dist_group_{i}')
    #                 subject_id = request.POST.get(f'dist_subject_{i}')
    #                 dist_id = request.POST.get(f'distribution_id_{i}')
    #                 dist_id_add = request.POST.get(f'distribution_id_{i}_add')
                    
    #                 if group_id and subject_id:
    #                     dist_data = {
    #                         "fk_group_id": group_id,
    #                         "fk_teacher_id": teacher_id,
    #                         "fk_subject_id": subject_id,
    #                     }

    #                     try:
    #                         if dist_id:
    #                             api_put(f"{self.endpoints['distributions']}{dist_id}/", dist_data)
    #                         elif dist_id_add:
    #                             api_post(self.endpoints["distributions"], dist_data)
    #                         else:
    #                             api_post(self.endpoints["distributions"], dist_data)
    #                     except Exception as e:
    #                         handle_exception(request, f"فشل حفظ توزيع رقم {i}", e)
    #                 else:
    #                     break

    #             messages.success(request, "تم حفظ المقررات بنجاح.")

    #         elif form_type == "times_form":
    #             for i in range(1, 100):
    #                 day_id = request.POST.get(f'time_day_{i}')
    #                 period_id = request.POST.get(f'time_period_{i}')
    #                 availability_id = request.POST.get(f'availability_id_{i}')
    #                 availability_id_add = request.POST.get(f'availability_id_{i}_add')

    #                 if day_id and period_id:
    #                     time_data = {
    #                         "fk_today_id": day_id,
    #                         "fk_period_id": period_id,
    #                         "fk_teacher_id": teacher_id,
    #                     }
                        
    #                     try:
    #                         if availability_id:
    #                             api_put(f"{self.endpoints['teacher_times']}{availability_id}/", time_data)
    #                         elif availability_id_add:
    #                             api_post(self.endpoints["teacher_times"], time_data)
                                
    #                         else:
    #                             api_post(self.endpoints["teacher_times"], time_data)
    #                     except Exception as e:
    #                         handle_exception(request, f"فشل حفظ وقت رقم {i}", e)
    #                 else:
    #                     break

    #             messages.success(request, "تم حفظ الأوقات المتاحة بنجاح.")

    #         else:
    #             messages.error(request, "نوع النموذج غير معروف.")

    #         return redirect("add_edit_teacher_with_courses", id=teacher_id)

    #     except Exception as e:
    #         handle_exception(request, "حدث خطأ أثناء الحفظ", e)
    #         return redirect(request.path_info)

def delete_teacher_with_courses_view(request, pk):
    if request.method == 'POST':
        print(f"تم حذف المدرس ذو الـ ID: {pk}")
        return redirect('teachers_management')
    
    context = {
        'page_title': 'تأكيد حذف المدرس',
        'teacher': {'id': pk, 'name': f'المدرس ذو الـ ID: {pk}'}
    }
    return render(request, 'teachers/confirm_delete_teacher_with_courses.html', context)

class CoursesView(View):
    endpoints = {
        "levels": "levels/",
        "subjects": "subjects/",
    }

    def get(self, request, id=None):
        try:
            if id:
                subject = api_get(f"{self.endpoints['subjects']}{id}/")
                levels = api_get(self.endpoints["levels"])
                return render(request, "courses/add_edit.html", context={
                    "subject": subject,
                    "levels": levels,
                    "page_title": "تعديل"
                })

            elif "add" in request.GET:
                levels = api_get(self.endpoints["levels"])
                return render(request, "courses/add_edit.html", context={
                    "levels": levels,
                    "page_title": "إضافة مقرر"
                })

            else:
                subjects = api_get(self.endpoints["subjects"])

                # احصائيات (يمكن تعديلها حسب بياناتك)
                total_courses = len(subjects)
                active_courses = sum(1 for c in subjects if c.get("active", True))
                full_courses = sum(1 for c in subjects if c.get("is_full", False))

                csrf_token = get_token(request)

                return render(request, "courses/list.html", {
                    "courses": subjects,
                    "page_title": "إدارة المقررات",
                    "total_courses": total_courses,
                    "active_courses": active_courses,
                    "full_courses": full_courses,
                    "csrf_token": csrf_token,
                })

        except Exception as e:
            handle_exception(request, "فشل في تحميل البيانات", e)
            return render(request, "courses/list.html", {"error": str(e)})

    def post(self, request, id=None):
        form_action = request.POST.get("form_action", "create")

        data = {
            "subject_name": request.POST.get("subject_name"),
            "fk_level_id": request.POST.get("fk_level"),
            "term": request.POST.get("term"),
        }

        try:
            if form_action == "delete" and id:
                api_delete(f"{self.endpoints['subjects']}{id}/")
                messages.success(request, "تم حذف المقرر بنجاح.")

            elif id:
                api_put(f"{self.endpoints['subjects']}{id}/", data)
                messages.success(request, "تم تعديل المقرر بنجاح.")

            else:
                api_post(self.endpoints["subjects"], data)
                messages.success(request, "تم إضافة المقرر بنجاح.")

            return redirect("courses_list")

        except Exception as e:
            handle_exception(request, "حدث خطأ أثناء حفظ البيانات", e)
            return redirect(request.path_info)

class CoursesView(View):
    endpoints = {
        "levels": "levels/",
        "subjects": "subjects/",
    }

    def get(self, request, id=None):
        try:
            if id:
                subject = api_get(f"{self.endpoints['subjects']}{id}/")
                levels = api_get(self.endpoints["levels"])
                return render(request, "courses/add_edit.html", context={
                    "subject": subject,
                    "levels": levels,
                    "page_title": "تعديل"
                })

            elif "add" in request.GET:
                levels = api_get(self.endpoints["levels"])
                return render(request, "courses/add_edit.html", context={
                    "levels": levels,
                    "page_title": "إضافة مقرر"
                })

            else:
                subjects = api_get(self.endpoints["subjects"])
                total_courses = len(subjects)
                active_courses = sum(1 for c in subjects if c.get("active", True))
                full_courses = sum(1 for c in subjects if c.get("is_full", False))

                csrf_token = get_token(request)

                return render(request, "courses/list.html", {
                    "courses": subjects,
                    "page_title": "إدارة المقررات",
                    "total_courses": total_courses,
                    "active_courses": active_courses,
                    "full_courses": full_courses,
                    "csrf_token": csrf_token,
                })

        except Exception as e:
            handle_exception(request, "فشل في تحميل البيانات", e)
            return render(request, "courses/list.html", {"error": str(e)})

    def post(self, request, id=None):
        form_action = request.POST.get("form_action", "create")

        data = {
            "subject_name": request.POST.get("subject_name"),
            "fk_level_id": request.POST.get("fk_level"),
            "term": request.POST.get("term"),
        }

        try:
            if form_action == "delete" and id:
                api_delete(f"{self.endpoints['subjects']}{id}/")
                messages.success(request, "تم حذف المقرر بنجاح.")
                return redirect("courses_management")

            elif id:
                api_put(f"{self.endpoints['subjects']}{id}/", data)
                messages.success(request, "تم تعديل المقرر بنجاح.")

            else:
                api_post(self.endpoints["subjects"], data)
                messages.success(request, "تم إضافة المقرر بنجاح.")

            return redirect("courses_management")

        except Exception as e:
            handle_exception(request, "حدث خطأ أثناء حفظ البيانات", e)
            return redirect(request.path_info)


def course_form_view(request, pk=None):
    """
    دالة موحدة لإضافة/تعديل المقررات (اسم المقرر فقط).
    """
    course = None

    if pk: # وضع التعديل
        page_title = 'تعديل المقرر'
        course = {
            'id': pk,
            'name': 'رياضيات متقدمة', # مثال
        }
    else: # وضع الإضافة
        page_title = 'إضافة مقرر جديد'
        course = {
            'id': None,
            'name': '',
        }
    
    if request.method == 'POST':
        course_name = request.POST.get('name')
        if pk:
            print(f"تم حفظ تعديلات المقرر (ID: {pk}): {course_name}")
        else:
            print(f"تم إضافة مقرر جديد: {course_name}")
        return redirect('courses_list')

    context = {
        'page_title': page_title,
        'course': course,
    }
    return render(request, 'courses/add_edit.html', context)

def delete_course_view(request, pk):
    if request.method == 'POST':
        print(f"تم حذف المقرر ذو الـ ID: {pk}")
        return redirect('courses_management')
    
    context = {
        'page_title': 'تأكيد حذف المقرر',
        'course': {'id': pk, 'name': 'المقرر المراد حذفه (اسم وهمي)'}
    }
    return render(request, 'courses/confirm_delete.html', context)

# --- بيانات وهمية بسيطة للقاعات (للعرض فقط) ---
dummy_rooms_data = {
    1: {'id': 1, 'name': 'القاعة الرئيسية (أ)', 'capacity': 50, 'status': 'متاحة'},
    2: {'id': 2, 'name': 'قاعة الاجتماعات (ب)', 'capacity': 20, 'status': 'مشغولة'},
    3: {'id': 3, 'name': 'المعمل الرقمي (ج)', 'capacity': 30, 'status': 'تحت الصيانة'},
    4: {'id': 4, 'name': 'قاعة الدورات (د)', 'capacity': 25, 'status': 'متاحة'},
    5: {'id': 5, 'name': 'استوديو التسجيل (هـ)', 'capacity': 10, 'status': 'مشغولة'},
}

# --- دوال عرض القاعات (Views) المبسطة ---

def rooms_management_view(request):
    """
    تعرض صفحة إدارة القاعات الرئيسية وقائمة القاعات، بالإضافة إلى إحصائيات.
    """
    rooms = list(dummy_rooms_data.values())

    # حساب الإحصائيات
    total_rooms = len(rooms)
    available_rooms = sum(1 for room in rooms if room['status'] == 'متاحة')
    occupied_rooms = sum(1 for room in rooms if room['status'] == 'مشغولة')
    maintenance_rooms = sum(1 for room in rooms if room['status'] == 'تحت الصيانة')

    stats = {
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'occupied_rooms': occupied_rooms,
        'maintenance_rooms': maintenance_rooms,
    }

    context = {
        'page_title': 'إدارة القاعات',
        'rooms': rooms,
        'stats': stats, # تمرير كائن الإحصائيات إلى القالب
    }
    return render(request, 'rooms/list.html', context)

def add_edit_room_view(request, pk=None):
    """
    تعرض صفحة إضافة قاعة جديدة أو تعديل قاعة موجودة.
    لا تقوم بعمليات حفظ أو تحديث فعلية.
    """
    room = None
    if pk:
        room = dummy_rooms_data.get(pk)
        if not room:
            return redirect('rooms_management')

    if request.method == 'POST':
        print(f"تم استقبال بيانات POST لـ {'التعديل' if pk else 'الإضافة'} (القاعة): {request.POST}")
        return redirect('rooms_management')

    context = {
        'page_title': 'إدارة القاعة',
        'room': room
    }
    return render(request, 'rooms/add_edit.html', context)

def confirm_delete_room_view(request, pk):
    """
    تعرض صفحة تأكيد حذف قاعة.
    لا تقوم بعملية حذف فعلية.
    """
    room = dummy_rooms_data.get(pk)
    if not room:
        return redirect('rooms_management')

    if request.method == 'POST':
        print(f"تم تأكيد طلب حذف القاعة ID: {pk}")
        return redirect('rooms_management')

    context = {
        'page_title': 'تأكيد حذف القاعة',
        'room': room
    }
    return render(request, 'rooms/confirm_delete.html', context)



from django.shortcuts import render, redirect

# --- بيانات وهمية (Dummy Data) ---
# في تطبيق حقيقي، ستأتي هذه البيانات من قاعدة البيانات الخاصة بك (نماذج Django).

dummy_courses_for_dropdown = [
    {'id': 1, 'name': 'الرياضيات المتقدمة', 'code': 'MATH301'},
    {'id': 2, 'name': 'اللغة الإنجليزية للمبتدئين', 'code': 'ENG101'},
    {'id': 3, 'name': 'مقدمة في البرمجة', 'code': 'CS100'},
    {'id': 4, 'name': 'تاريخ الحضارات', 'code': 'HIST200'},
    {'id': 5, 'name': 'الخوارزميات وهياكل البيانات', 'code': 'CS201'},
    {'id': 6, 'name': 'شبكات الحاسوب', 'code': 'NET302'},
    {'id': 7, 'name': 'قواعد البيانات', 'code': 'DB301'},
    {'id': 8, 'name': 'الأمن السيبراني', 'code': 'CYB401'},
    {'id': 9, 'name': 'الفيزياء 101', 'code': 'PHY101'},
    {'id': 10, 'name': 'مبادئ الاقتصاد', 'code': 'ECON201'},
]

dummy_departments_data = {
    1: {
        'id': 1,
        'name': 'علوم الحاسب',
        'description': 'تخصص يركز على دراسة الحوسبة ونظم المعلومات.',
        # 'total_students' و 'num_courses' سيتم حسابهما ديناميكيًا
        'num_levels': 4, # هذا ثابت لتبسيط المثال، يتطلب منطقًا لإنشاء/حذف مستويات فعلية
        'levels_data': [
            {'level_id': 101, 'name': 'المستوى الأول (CS)', 'num_students': 80, 'associated_courses_ids': [3, 4, 7]},
            {'level_id': 102, 'name': 'المستوى الثاني (CS)', 'num_students': 70, 'associated_courses_ids': [1, 5, 6]},
            {'level_id': 103, 'name': 'المستوى الثالث (CS)', 'num_students': 60, 'associated_courses_ids': [8, 1, 3]},
            {'level_id': 104, 'name': 'المستوى الرابع (CS)', 'num_students': 40, 'associated_courses_ids': [5, 6, 7, 8]},
        ]
    },
    2: {
        'id': 2,
        'name': 'هندسة البرمجيات',
        'description': 'تخصص يهتم بتصميم وتطوير البرمجيات.',
        'num_levels': 4,
        'levels_data': [
            {'level_id': 201, 'name': 'المستوى الأول (SE)', 'num_students': 60, 'associated_courses_ids': [3, 4]},
            {'level_id': 202, 'name': 'المستوى الثاني (SE)', 'num_students': 50, 'associated_courses_ids': [1, 5]},
            {'level_id': 203, 'name': 'المستوى الثالث (SE)', 'num_students': 40, 'associated_courses_ids': [6, 7]},
            {'level_id': 204, 'name': 'المستوى الرابع (SE)', 'num_students': 30, 'associated_courses_ids': [8]},
        ]
    },
    3: {
        'id': 3,
        'name': 'نظم المعلومات',
        'description': 'الجمع بين الأعمال والتكنولوجيا لإدارة البيانات.',
        'num_levels': 3,
        'levels_data': [
            {'level_id': 301, 'name': 'المستوى الأول (IS)', 'num_students': 50, 'associated_courses_ids': [2, 3]},
            {'level_id': 302, 'name': 'المستوى الثاني (IS)', 'num_students': 40, 'associated_courses_ids': [6, 7]},
            {'level_id': 303, 'name': 'المستوى الثالث (IS)', 'num_students': 30, 'associated_courses_ids': [8]},
        ]
    },
}

# --- دوال مساعدة (Helper Functions) ---
def get_course_details(course_id):
    """
    تعيد اسم المقرر وكوده لمعرف مقرر معين.
    """
    for course in dummy_courses_for_dropdown:
        if course['id'] == course_id:
            return {'id': course['id'], 'name': f"{course['name']} ({course['code']})"}
    return {'id': course_id, 'name': "مقرر غير معروف"}

# --- دوال العرض (View Functions) ---

# دالة لوحة التحكم - لا يوجد تغيير هنا من الردود السابقة
def dashboard_view(request):
    """
    تعرض لوحة التحكم الرئيسية بإحصائيات مجمعة.
    """
    total_departments = len(dummy_departments_data)
    total_students = 0
    total_teachers = 15 # قيمة وهمية
    total_courses = len(dummy_courses_for_dropdown) # جميع المقررات المتاحة
    total_levels = 0 # سيتم عد المستويات عبر جميع الأقسام

    for dept_id, dept_data in dummy_departments_data.items():
        total_students += sum(level['num_students'] for level in dept_data['levels_data'])
        total_levels += len(dept_data['levels_data'])

    stats = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_departments': total_departments,
        'total_levels': total_levels,
        'total_courses': total_courses,
    }

    context = {
        'page_title': 'لوحة التحكم الرئيسية',
        'stats': stats,
    }
    return render(request, 'dashboard.html', context)


# دالة إدارة الأقسام - لا يوجد تغيير هنا من الردود السابقة
def departments_management_view(request):
    """
    تعرض صفحة إدارة الأقسام الرئيسية وقائمة بالأقسام.
    تحسب الإحصائيات الديناميكية لكل قسم.
    """
    departments = list(dummy_departments_data.values())

    overall_total_students = 0
    overall_total_courses = 0

    for dept in departments:
        # حساب إجمالي الطلاب لهذا القسم بناءً على مستوياته
        dept_total_students = sum(level['num_students'] for level in dept['levels_data'])
        dept['total_students'] = dept_total_students
        overall_total_students += dept_total_students

        # حساب المقررات الفريدة التي يتم تدريسها عبر جميع المستويات في هذا القسم
        dept_unique_courses_ids = set()
        for level in dept['levels_data']:
            dept_unique_courses_ids.update(level['associated_courses_ids'])
        dept['num_courses'] = len(dept_unique_courses_ids) # هذا هو عدد المقررات الفريدة للقسم
        overall_total_courses += dept['num_courses'] # مجموع المقررات الفريدة لكل قسم

    stats = {
        'total_departments': len(departments),
        'overall_total_students': overall_total_students,
        'overall_total_courses': overall_total_courses,
    }

    context = {
        'page_title': 'إدارة التخصصات والأقسام',
        'departments': departments,
        'stats': stats,
    }
    return render(request, 'departments/list.html', context)

# دالة إضافة/تعديل قسم - هذا هو الجزء الذي تم تحديثه
def add_edit_department_view(request, pk=None):
    """
    تتولى إضافة قسم جديد أو تعديل قسم موجود.
    تدير هذه الدالة تفاصيل القسم، وعدد الطلاب لكل مستوى،
    والمقررات المرتبطة بكل مستوى.
    """
    department = None
    if pk: # وضع التعديل
        department = dummy_departments_data.get(pk)
        if not department:
            return redirect('departments_management')

    if request.method == 'POST':
        if pk: # تحديث قسم موجود
            department_obj = dummy_departments_data[pk]
            department_obj['name'] = request.POST.get('department_name')
            department_obj['description'] = request.POST.get('description')
            # 'num_levels' تُرك ثابتًا لتبسيط المثال، حيث أن إضافة/حذف المستويات ديناميكيًا
            # مع بيانات وهمية يكون معقدًا ويتطلب منطقًا إضافيًا لإنشاء/حذف كيانات مستوى فعلية.

            updated_levels_data = []
            # المرور على المستويات الموجودة لتحديث بيانات الطلاب والمقررات
            for level_data_old in department_obj['levels_data']:
                level_id = level_data_old['level_id']
                
                # جلب عدد الطلاب لهذا المستوى
                num_students = int(request.POST.get(f"level_{level_id}_students", 0))

                # جلب معرفات المقررات المرتبطة بهذا المستوى.
                # request.POST.getlist() يستخدم لأن المقررات تُرسل كمدخلات متعددة بنفس الاسم.
                associated_courses = [
                    int(cid) for cid in request.POST.getlist(f"level_{level_id}_courses[]") if cid.isdigit()
                ]

                updated_levels_data.append({
                    'level_id': level_id,
                    'name': level_data_old['name'], # الاحتفاظ بالاسم الحالي للمستوى
                    'num_students': num_students,
                    'associated_courses_ids': associated_courses,
                })
            
            department_obj['levels_data'] = updated_levels_data

            # إعادة حساب إجمالي الطلاب للقسم
            department_obj['total_students'] = sum(level['num_students'] for level in department_obj['levels_data'])
            
            # إعادة حساب المقررات الفريدة للقسم
            dept_unique_courses = set()
            for level in department_obj['levels_data']:
                dept_unique_courses.update(level['associated_courses_ids'])
            department_obj['num_courses'] = len(dept_unique_courses)

        else: # إضافة قسم جديد (تبسيط شديد لغرض البيانات الوهمية)
            new_id = max(dummy_departments_data.keys()) + 1 if dummy_departments_data else 1
            new_department = {
                'id': new_id,
                'name': request.POST.get('department_name'),
                'description': request.POST.get('description'),
                'total_students': 0, # سيتم حسابها إذا تم إضافة مستويات
                'num_levels': 0, # مؤقت
                'num_courses': 0, # سيتم حسابها إذا تم إضافة مستويات ومقررات
                'levels_data': [], # يجب إضافة منطق لإنشاء مستويات افتراضية هنا بناءً على 'num_levels' إذا كان مدخلًا
            }
            dummy_departments_data[new_id] = new_department

        return redirect('departments_management')

    # لطلبات GET (عرض النموذج)
    all_courses_for_dropdown = dummy_courses_for_dropdown
    
    if department:
        for level in department['levels_data']:
            # إعداد تفاصيل المقررات الحالية في هذا المستوى لعرضها
            current_courses_details = []
            for course_id in level.get('associated_courses_ids', []):
                current_courses_details.append(get_course_details(course_id))
            level['current_courses_details'] = current_courses_details

    context = {
        'page_title': 'إدارة القسم/التخصص',
        'department': department,
        'all_courses': all_courses_for_dropdown, # جميع المقررات المتاحة للإضافة
    }
    return render(request, 'departments/add_edit.html', context)

# دالة حذف قسم - لا يوجد تغيير هنا من الردود السابقة
def delete_department_view(request, pk):
    """
    تتولى حذف قسم (تُفعل بطلب POST من النافذة المنبثقة).
    """
    if request.method == 'POST':
        if pk in dummy_departments_data:
            del dummy_departments_data[pk]
            print(f"تم حذف القسم ذو المعرف {pk} (وهمي).")
        return redirect('departments_management')
    # إذا وصل طلب GET هنا (مثلاً، وصول مباشر)، أعد التوجيه
    return redirect('departments_management')



# my_app/views.py

from . import utlis # استيراد البيانات الوهمية من الملف الجديد

def add_edit_session_view(request, session_id=None):
    """
    يعرض نموذج إضافة أو تعديل حصة دراسية.
    session_id=None للإضافة، وإلا فهو للتعديل.
    """
    session_data = None
    if session_id:
        page_title = f"تعديل حصة دراسية"
        # في التطبيق الحقيقي، هنا ستجلب بيانات الحصة من قاعدة البيانات بناءً على session_id
        # للتصميم، نستخدم البيانات الوهمية المعدة مسبقًا
        session_data = utlis.dummy_session_for_edit
    else:
        page_title = "إضافة حصة دراسية جديدة"

    context = {
        'page_title': page_title,
        'courses': utlis.dummy_courses_for_dropdown,
        'teachers': utlis.dummy_teachers,
        'rooms': utlis.dummy_rooms,
        'levels': utlis.get_all_levels(), # استخدم الدالة من utlis
        'all_days_of_week': ['الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت'],
        'session_data': session_data, # تمرير بيانات الحصة للتعديل (إن وجدت)
        'is_edit_mode': session_id is not None,
    }
    return render(request, 'timetable/add_edit_session.html', context)

# ... (باقي دوال الـ views الموجودة لديك) ...

# مثال لدالة timetable_settings_view بعد نقل البيانات (إن كنت قد وضعتها فيها)
def timetable_settings_view(request):
    context = {
        'page_title': 'إعدادات الجدول الزمني',
        'settings': {
            'working_days': ['الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس'],
            'start_of_day': '08:00',
            'end_of_day': '16:00',
            'break_time_start': '12:00',
            'break_time_end': '13:00',
            'class_duration_minutes': 90,
            'buffer_minutes_between_classes': 10,
        },
        'all_days_of_week': ['الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت'],
    }
    return render(request, 'timetables/list.html', context)