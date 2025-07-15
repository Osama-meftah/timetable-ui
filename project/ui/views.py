from django.shortcuts import render, redirect
from django.views import View
import requests
from django.contrib import messages
from .utils import *
from django.middleware.csrf import get_token
from collections import Counter


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

class TeacherManagementView(View):
    def get(self, request, id=None):
        try:
            if id:
                teacher = api_get(f"{Endpoints.teachers}{id}/")
                return render(request, "teachers/add_edit.html", {"teacher": teacher})
            elif "add" in request.GET:
                return render(request, "teachers/add_edit.html", {"page_title": "إضافة مدرس"})

            # جلب البيانات
            teachers_data = api_get(Endpoints.teachers)

            teacher_times_data = api_get(Endpoints.teacher_times)
            distributions_data = api_get(Endpoints.distributions)
            print(distributions_data)
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
                        # "period": f"{datetime.strptime(t['fk_period']['period_from'], '%H:%M').strftime('%I:%M %p')} - {datetime.strptime(t['fk_period']['period_to'], '%H:%M').strftime('%I:%M %p')}"
                        "period": f"{t['fk_period']['period_from']} - {t['fk_period']['period_to']}"

                        # "period": t["fk_period"]["period_display"]
                    }
                    for t in teacher_times_data
                    if t["fk_teacher"]["id"] == teacher_id
                ]

                if courses:
                    teachers_with_data.append({
                        "teacher": teacher,
                        "courses": courses,
                        "availability": times,
                    })

            # إحصائيات
            total_teachers = len(teachers_data)
            active_teachers = len([t for t in teachers_data if t.get("teacher_status") == "نشط"])
            on_leave_teachers = len([t for t in teachers_data if t.get("teacher_status") == "إجازة"])
            
            teachers_paginated = paginate_queryset(teachers_data, request, "page", "page_size",5)
            teachers_data_paginated = paginate_queryset(teachers_with_data, request, "page_detailed", "page_data_size")
            # print(teachers_with_data)
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

    def post(self, request, id=None):
        form_type = request.POST.get("form_type")
        teacher_data = {
            "id": id,
            "teacher_name": request.POST.get("teacher_name", "").strip(),
            "teacher_phone": request.POST.get("teacher_phone", "").strip(),
            "teacher_email": request.POST.get("teacher_email", "").strip(),
            "teacher_address": request.POST.get("teacher_address", "").strip(),
            "teacher_status": request.POST.get("teacher_status", "").strip(),
        }

        # if not teacher_data["teacher_name"] or not teacher_data["teacher_email"]:
        #     messages.error(request, "الاسم والبريد الإلكتروني مطلوبان.")
        #     return redirect(request.path_info)

        try:
            if id:
                api_put(f"{Endpoints.teachers}{id}/", teacher_data)
                messages.success(request, "✅ تم تعديل بيانات المدرس.")
                return render(request, "teachers/add_edit.html", context={"teacher": teacher_data})
            elif form_type == "upload_teachers":
                handle_file_upload_generic(
                request,
                file_field_name='data_file',
                endpoint_url=f"{BASE_API_URL}{Endpoints.teachersUpload}",
                success_title="✅ تم رفع ملف المدرسين بنجاح.",
                error_title="❌ فشل رفع ملف المدرسين"
                )
                return redirect(request.path_info)
            else:
                api_post(Endpoints.teachers, teacher_data)
                messages.success(request, "✅ تم إضافة المدرس.")
                return redirect("teachers_management")
            
        except Exception as e:
            messages.error(request, f"❌ حدث خطأ أثناء حفظ بيانات المدرس: {str(e)}")
            return redirect("teachers_management")


class TeacherDeleteView(View):
    def post(self, request, id):
        try:
            api_delete(f"{Endpoints.teachers}{id}/")
            messages.success(request, "تم حذف المدرس بنجاح.")
        except Exception as e:
            handle_exception(request, "حدث خطأ أثناء حذف المدرس", e)
        return redirect("teachers_management")


class TeacherAvailabilityAndCoursesView(View):
    def get(self, request, id=None):
        try:
            teachers = api_get(Endpoints.teachers)
            days = api_get(Endpoints.todays)
            periods = api_get(Endpoints.periods)
            subjects = api_get(Endpoints.subjects)
            levels = api_get(Endpoints.levels)
            programs =api_get(Endpoints.programs)
            groups = api_get(Endpoints.groups)
            # print(len(teachers))
            teacher = None
            teacher_times = []
            teacher_distributions = []
            # print(periods)
            if id:
                teacher =api_get(f"{Endpoints.teachers}{id}") 

                all_times = api_get(f"{Endpoints.teacher_times}")
                teacher_times = [t for t in all_times if t["fk_teacher"]["id"] == int(id)]

                all_distributions = api_get(f"{Endpoints.distributions}")
                # requests.get(f"{BASE_API_URL}{self.endpoints['distributions']}").json()
                teacher_distributions = [d for d in all_distributions if d["fk_teacher"]["id"] == int(id)]
                # print(teacher_distributions)
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
            # if not teacher_id:
            #     messages.error(request, "يرجى اختيار المدرس.")
            #     return redirect(request.path_info)

            try:
                if form_type == "courses_form":
                    for i in range(1, 100):
                        group_id = request.POST.get(f'dist_group_{i}')
                        subject_id = request.POST.get(f'dist_subject_{i}')
                        dist_id = request.POST.get(f'distribution_id_{i}')
                        print(f"Group ID: {group_id}, Subject ID: {subject_id}, Distribution ID: {dist_id}")
                        
                        if group_id and subject_id:
                            dist_data = {
                                "fk_group_id": group_id,
                                "fk_teacher_id": teacher_id,
                                "fk_subject_id": subject_id,
                            }

                            try:
                                if dist_id:
                                    api_put(f"{Endpoints.distributions}{dist_id}/", dist_data)
                                else:
                                    api_post(Endpoints.distributions, dist_data)
                            except Exception as e:
                                handle_exception(request, f"فشل حفظ توزيع رقم {i}", e)

                    # ✅ ضع الـ redirect هنا بعد انتهاء كل العمليات
                    return redirect("add_edit_teacher_with_courses", id=teacher_id)
                elif form_type == "times_form":
                    for i in range(1, 100):
                        day_id = request.POST.get(f'time_day_{i}')
                        period_id = request.POST.get(f'time_period_{i}')
                        availability_id = request.POST.get(f'availability_id_{i}')
                        print(f"alfjasljdf{availability_id}")
                        if day_id and period_id:
                            time_data = {
                                "fk_today_id": day_id,
                                "fk_period_id": period_id,
                                "fk_teacher_id": teacher_id,
                            }
                            print(time_data)
                            try:
                                if availability_id:
                                    print(time_data)
                                    api_put(f"{Endpoints.teacher_times}{availability_id}/", time_data)
                                else:
                                    print(time_data)
                                    api_post(Endpoints.teacher_times, time_data)
                                    messages.success(request, "تم حفظ الأوقات المتاحة بنجاح.")
                            except Exception as e:
                                handle_exception(request, f"فشل حفظ وقت رقم {i}", e)
                        else:
                            break

                    
                elif form_type == "delete_distribution":
                    print("============================")
                    dist_id = request.POST.get("item_id")
                    if dist_id:
                        try:
                            api_delete(f"{Endpoints.distributions}{dist_id}/")
                            messages.success(request, "تم حذف توزيع المقرر بنجاح.")
                        except Exception as e:
                            handle_exception(request, "فشل في حذف توزيع المقرر", e)

                elif form_type == "delete_availability":
                    print("============================")
                    availability_id = request.POST.get("item_id")
                    print(f"Availability ID: {availability_id}")
                    if availability_id:
                        try:
                            api_delete(f"{Endpoints.teacher_times}{availability_id}/")
                            messages.success(request, "تم حذف وقت التوفر بنجاح.")
                        except Exception as e:
                            handle_exception(request, "فشل في حذف وقت التوفر", e)

                else:
                    messages.error(request, "نوع النموذج غير معروف.")

                return redirect("add_edit_teacher_with_courses", id=teacher_id)

            except Exception as e:
                handle_exception(request, "حدث خطأ أثناء الحفظ", e)
                return redirect(request.path_info)
            

class CoursesView(View):
    def get(self, request, id=None):
        try:
            if id:
                subject = api_get(f"{Endpoints.subjects}{id}/")
                levels = api_get(Endpoints.levels)
                return render(request, "courses/add_edit.html", context={
                    "subject": subject,
                    "levels": levels,
                    "page_title": "تعديل"
                })

            elif "add" in request.GET:
                levels = api_get(Endpoints.levels)
                return render(request, "courses/add_edit.html", context={
                    "levels": levels,
                    "page_title": "إضافة مقرر"
                })

            else:
                subjects = api_get(Endpoints.subjects)

                total_courses = len(subjects)
                active_courses = sum(1 for c in subjects if c.get("active", True))
                full_courses = sum(1 for c in subjects if c.get("is_full", False))

                csrf_token = get_token(request)
                subjects_paginated = paginate_queryset(subjects, request, "page", "page_size",5)

                return render(request, "courses/list.html", {
                    "courses": subjects_paginated,
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
        form_type = request.POST.get("form_type", "create")

        data = {
            "subject_name": request.POST.get("subject_name"),
            "term": request.POST.get("term"),
        }
        try:
            # print(form_type)
            if form_type == "delete" and id:
                print(id)
                api_delete(f"{Endpoints.subjects}{id}/")
                messages.success(request, "تم حذف المقرر بنجاح.")
            elif form_type == 'upload_subjects':
                handle_file_upload_generic(
                    request,
                    file_field_name='data_file',
                    endpoint_url=f"{BASE_API_URL}{Endpoints.uploadSubjects}",
                    success_title="✅ تم رفع ملف البرامج بنجاح.",
                    error_title="❌ فشل رفع ملف البرامج"
                )
            elif id and form_type == "edit":
                api_put(f"{Endpoints.subjects}{id}/", data)
                messages.success(request, "تم تعديل المقرر بنجاح.")

            elif form_type == "add":
                api_post(Endpoints.subjects, data)
                messages.success(request, "تم إضافة المقرر بنجاح.")
            else:
                return redirect("courses_management")
                # messages.error(request, "نوع النموذج غير معروف أو البيانات غير مكتملة.")
            return redirect("courses_management")

        except Exception as e:
            handle_exception(request, "حدث خطأ أثناء حفظ البيانات", e)
            return redirect(request.path_info)
        
class RoomsView(View):
    def get(self, request, id=None):
        if id:
            room = api_get(f"{Endpoints.halls}{id}/")
            print(room)
            return render(request, 'rooms/add_edit.html', {"room": room})
        elif "add" in request.GET:
            return render(request, 'rooms/add_edit.html')
        else:
            rooms = api_get(Endpoints.halls)
            total_rooms = len(rooms)
            maintenance_rooms = sum(1 for room in rooms if room['hall_status'] == 'تحت الصيانة')

            largest_capacity_room = max(rooms, key=lambda r: r['capacity_hall'], default=None)

            capacity_list = [room['capacity_hall'] for room in rooms]
            capacity_counts = dict(Counter(capacity_list))
            stats = {
                'total_rooms': total_rooms,
                'maintenance_rooms': maintenance_rooms,
                'largest_capacity_room': largest_capacity_room,
                'capacity_counts': capacity_counts,
            }
            room_paginated = paginate_queryset(rooms, request, "page", "page_size",8)

            context = {
                'page_title': 'إدارة القاعات',
                'rooms': room_paginated,
                'stats': stats,
            }

            return render(request, 'rooms/list.html', context)
       
    def post(self, request, id=None):
        form_type = request.POST.get('form_type')

        if form_type == 'add':
            new_room_data = {
                "hall_name": request.POST.get("name"),
                "capacity_hall": int(request.POST.get("capacity")),
                "hall_status": request.POST.get("status"),
            }
            try:
                api_post(Endpoints.halls, new_room_data)
                messages.success(request, "تم إضافة القاعة بنجاح.")
            except RuntimeError as e:
                messages.error(request, f"خطأ في إضافة القاعة: {e}")
        elif form_type == 'upload_rooms':
            handle_file_upload_generic(
                    request,
                    file_field_name='data_file',
                    endpoint_url=f"{BASE_API_URL}{Endpoints.uploadHalls}",
                    success_title="✅ تم رفع ملف البرامج بنجاح.",
                    error_title="❌ فشل رفع ملف البرامج"
                )
        elif form_type == 'edit':
            room_id = request.POST.get("room_id")
            updated_data = {
                "hall_name": request.POST.get("name"),
                "capacity_hall": int(request.POST.get("capacity")),
                "hall_status": request.POST.get("status"),
            }
            try:
                api_put(f"{Endpoints.halls}{room_id}/", updated_data)
                messages.success(request, "تم تحديث بيانات القاعة بنجاح.")
            except RuntimeError as e:
                messages.error(request, f"خطأ في تحديث القاعة: {e}")

        elif form_type == 'delete':
            room_id = request.POST.get("item_id")
            try:
                api_delete(f"{Endpoints.halls}{id}/")
                messages.success(request, "تم حذف القاعة بنجاح.")
            except RuntimeError as e:
                messages.error(request, f"خطأ في حذف القاعة: {e}")

        else:
            messages.error(request, "إجراء غير معروف.")

        return redirect('rooms_management')

class DepartmentsManagementView(View):
    def get(self, request, id=None):
        try:
            if id:
                dept = api_get(f"{Endpoints.departments}{id}/")
                return render(request, 'departments/add_edit.html', {"department": dept})

            elif "add" in request.GET:
                return render(request, 'departments/add_edit.html')

            dept = api_get(Endpoints.departments)
            programs = api_get(Endpoints.programs)
            levels = api_get(Endpoints.levels)

            programs_with_levels = []
            for program in programs:
                program_levels = [level for level in levels if level["fk_program"]["id"] == program["id"]]
                programs_with_levels.append({
                    "program": program,
                    "levels": program_levels,
                })

            for d in dept:
                d["programs"] = [p for p in programs_with_levels if p["program"]["fk_department"]["id"] == d["id"]]

            stats = {
                'total_departments': len(dept),
                'overall_total_programs': len(programs),
                'overall_total_courses': len(levels),
            }
            print(dept)
            context = {
                'page_title': 'إدارة التخصصات والأقسام',
                'departments': dept,
                'programs': programs_with_levels,
                'stats': stats,
            }

            return render(request, 'departments/list.html', context)
        except Exception as e:
            context = {
                'page_title': 'إدارة التخصصات والأقسام',
                'departments': dept,
                'programs': programs_with_levels,
                'stats': stats,
            }
            handle_exception(request, "فشل في جلب البيانات", e)
            return render(request, 'departments/list.html', context)


        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء تحميل الصفحة: {e}")
            return redirect('departments_management')  # أو صفحة خطأ مناسبة

    def post(self, request, id=None):
        try:
            action = request.POST.get('form_type')

            if action == 'add':
                name = request.POST.get("department_name", "").strip()
                desc = request.POST.get("description", "").strip()

                if not name:
                    messages.error(request, "اسم القسم مطلوب.")
                    return redirect('departments_management')

                new_dept_data = {"name": name, "description": desc}
                api_post(Endpoints.departments, new_dept_data)
                messages.success(request, "تم إضافة قسم بنجاح.")
            
            elif action == 'upload_departments':
                handle_file_upload_generic(
                    request,
                    file_field_name='data_file',
                    endpoint_url=f"{BASE_API_URL}{Endpoints.departmentsUpload}",
                    success_title="✅ تم رفع ملف الأقسام بنجاح.",
                    error_title="❌ فشل رفع ملف الأقسام"
                )

            elif action == 'upload_programs':
                handle_file_upload_generic(
                    request,
                    file_field_name='data_file',
                    endpoint_url=f"{BASE_API_URL}{Endpoints.programsUpload}",
                    success_title="✅ تم رفع ملف البرامج بنجاح.",
                    error_title="❌ فشل رفع ملف البرامج"
                )

            elif action == 'edit':
                dept_id = request.POST.get("dept_id")
                name = request.POST.get("department_name", "").strip()
                desc = request.POST.get("description", "").strip()

                if not (dept_id and name):
                    messages.error(request, "يجب توفير رقم القسم واسم القسم.")
                    return redirect('departments_management')

                updated_dept_data = {"name": name, "description": desc}
                api_put(f"{Endpoints.departments}{dept_id}/", updated_dept_data)
                messages.success(request, "تم تحديث بيانات القسم بنجاح.")


            elif action == 'delete':
                if not id:
                    messages.error(request, "رقم القسم غير موجود.")
                    return redirect('departments_management')

                api_delete(f"{Endpoints.departments}{id}/")
                messages.success(request, "تم حذف القسم بنجاح.")

            else:
                messages.error(request, "إجراء غير معروف.")

        except RuntimeError as e:
            messages.error(request, f"خطأ في التواصل مع الخادم: {e}")
        except Exception as e:
            messages.error(request, f"حدث خطأ غير متوقع: {e}")

        return redirect('departments_management')

class AddAndEditProgramView(View):
    def get(self, request, id=None):
        if id:
            program = api_get(f"{Endpoints.programs}{id}/")
            programs = api_get(f"{Endpoints.programs}")
            levels = api_get(f"{Endpoints.levels}")
            departments = api_get(f"{Endpoints.departments}")
            return render(request, 'programs/add_edit.html', {
                "program": program,
                "programs": programs,
                "levels": levels,
                "departments": departments,
                "page_title": "تعديل"
            })

        elif "add" in request.GET:
            programs = api_get(f"{Endpoints.programs}")
            levels = api_get(f"{Endpoints.levels}")
            departments = api_get(f"{Endpoints.departments}")
            return render(request, 'programs/add_edit.html', {
                "levels": levels,
                "programs": programs,
                "departments": departments,
                "page_title": "إضافة"
            })
        else:
            programs = api_get(f"{Endpoints.programs}")
            levels = api_get(f"{Endpoints.levels}")
            departments = api_get(f"{Endpoints.departments}")
            return render(request, 'programs/add_edit.html', {
                "levels": levels,
                "programs": programs,
                "departments": departments,
                "page_title": "إضافة"
            })
            
    def post(self, request, id=None):
        form_type = request.POST.get('form_type')
        print(form_type)
        if form_type == "program_form_submit":
            program_id = request.POST.get('program_id')
            program_name = request.POST.get('program_name')
            fk_department_id = request.POST.get('fk_department')
            data = {
                'program_name': program_name,
                'department_id': fk_department_id,
            }
            try:
                if program_id:
                    api_put(f"{Endpoints.programs}{program_id}/", data)
                    messages.success(request, "تم تحديث البرنامج بنجاح!")
                else:
                    api_post(f"{Endpoints.programs}", data)
                    messages.success(request, "تم إضافة البرنامج بنجاح!")
            except Exception as e:
                handle_exception(request, f"فشل حفظ البرنامج {data}", e)

            return redirect(request.path_info)

        elif form_type == "level_form_submit":
            level_id = request.POST.get('level_id')
            level_name = request.POST.get('level_name')
            number_students = request.POST.get('number_students')
            fk_program_id = request.POST.get('fk_program')
            level_data = {
                "level_name": level_name,
                "number_students": number_students,
                "fk_program_id": fk_program_id
            }
            try:
                if level_id:
                    api_put(f"{Endpoints.levels}{level_id}/", level_data)
                    messages.success(request, "تم تحديث المستوى بنجاح!")
                else:
                    api_post(f"{Endpoints.levels}", level_data)
                    messages.success(request, "تم إضافة المستوى بنجاح!")
            except Exception as e:
                handle_exception(request, f"فشل حفظ المستوى {level_data}", e)
            return redirect(request.path_info)
        
        elif form_type == 'upload_levels':
                handle_file_upload_generic(
                    request,
                    file_field_name='data_file',
                    endpoint_url=f"{BASE_API_URL}{Endpoints.levelsUpload}",
                    success_title="✅ تم رفع ملف البرامج بنجاح.",
                    error_title="❌ فشل رفع ملف البرامج"
                )
        print(form_type)
        if form_type =='delete':
            item_id = request.POST.get('item_id')
            item_type = request.POST.get('selected_level_or_program')
            try:
                if item_type == 'program':
                    api_delete(f"{Endpoints.programs}{item_id}/")
                    messages.success(request, f"تم حذف البرنامج '{item_type}' بنجاح.")
                elif item_type == 'level':
                    api_delete(f"{Endpoints.levels}{item_id}/")
                    messages.success(request, f"تم حذف المستوى '{item_type}' بنجاح.")
                    
            except Exception as e:
                messages.error(request, f"حدث خطأ أثناء الحذف: {e}")
                print(f"Error deleting item of type {item_type} with ID {item_id}: {e}")
            # return redirect(request.path_info) # ✅ تأكد من وجود redirect هنا أيضًا

        messages.error(request, "نوع النموذج غير معروف.")
        return redirect('add_program')

class TimeTableSettingsView(View):
    def get(self, request, id=None):
        return render(request, 'timetables/list.html')
    
    


# def timetable_settings_view(request):
#     context = {
#         'page_title': 'إعدادات الجدول الزمني',
#         'settings': {
#             'working_days': ['الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس'],
#             'start_of_day': '08:00',
#             'end_of_day': '16:00',
#             'break_time_start': '12:00',
#             'break_time_end': '13:00',
#             'class_duration_minutes': 90,
#             'buffer_minutes_between_classes': 10,
#         },
#         'all_days_of_week': ['الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت'],
#     }
#     return render(request, 'timetables/list.html', context)




# dummy_courses_for_dropdown = [
#     {'id': 1, 'name': 'الرياضيات المتقدمة', 'code': 'MATH301'},
#     {'id': 2, 'name': 'اللغة الإنجليزية للمبتدئين', 'code': 'ENG101'},
#     {'id': 3, 'name': 'مقدمة في البرمجة', 'code': 'CS100'},
#     {'id': 4, 'name': 'تاريخ الحضارات', 'code': 'HIST200'},
#     {'id': 5, 'name': 'الخوارزميات وهياكل البيانات', 'code': 'CS201'},
#     {'id': 6, 'name': 'شبكات الحاسوب', 'code': 'NET302'},
#     {'id': 7, 'name': 'قواعد البيانات', 'code': 'DB301'},
#     {'id': 8, 'name': 'الأمن السيبراني', 'code': 'CYB401'},
#     {'id': 9, 'name': 'الفيزياء 101', 'code': 'PHY101'},
#     {'id': 10, 'name': 'مبادئ الاقتصاد', 'code': 'ECON201'},
# ]

# dummy_departments_data = {
#     1: {
#         'id': 1,
#         'name': 'علوم الحاسب',
#         'description': 'تخصص يركز على دراسة الحوسبة ونظم المعلومات.',
#         # 'total_students' و 'num_courses' سيتم حسابهما ديناميكيًا
#         'num_levels': 4, # هذا ثابت لتبسيط المثال، يتطلب منطقًا لإنشاء/حذف مستويات فعلية
#         'levels_data': [
#             {'level_id': 101, 'name': 'المستوى الأول (CS)', 'num_students': 80, 'associated_courses_ids': [3, 4, 7]},
#             {'level_id': 102, 'name': 'المستوى الثاني (CS)', 'num_students': 70, 'associated_courses_ids': [1, 5, 6]},
#             {'level_id': 103, 'name': 'المستوى الثالث (CS)', 'num_students': 60, 'associated_courses_ids': [8, 1, 3]},
#             {'level_id': 104, 'name': 'المستوى الرابع (CS)', 'num_students': 40, 'associated_courses_ids': [5, 6, 7, 8]},
#         ]
#     },
#     2: {
#         'id': 2,
#         'name': 'هندسة البرمجيات',
#         'description': 'تخصص يهتم بتصميم وتطوير البرمجيات.',
#         'num_levels': 4,
#         'levels_data': [
#             {'level_id': 201, 'name': 'المستوى الأول (SE)', 'num_students': 60, 'associated_courses_ids': [3, 4]},
#             {'level_id': 202, 'name': 'المستوى الثاني (SE)', 'num_students': 50, 'associated_courses_ids': [1, 5]},
#             {'level_id': 203, 'name': 'المستوى الثالث (SE)', 'num_students': 40, 'associated_courses_ids': [6, 7]},
#             {'level_id': 204, 'name': 'المستوى الرابع (SE)', 'num_students': 30, 'associated_courses_ids': [8]},
#         ]
#     },
#     3: {
#         'id': 3,
#         'name': 'نظم المعلومات',
#         'description': 'الجمع بين الأعمال والتكنولوجيا لإدارة البيانات.',
#         'num_levels': 3,
#         'levels_data': [
#             {'level_id': 301, 'name': 'المستوى الأول (IS)', 'num_students': 50, 'associated_courses_ids': [2, 3]},
#             {'level_id': 302, 'name': 'المستوى الثاني (IS)', 'num_students': 40, 'associated_courses_ids': [6, 7]},
#             {'level_id': 303, 'name': 'المستوى الثالث (IS)', 'num_students': 30, 'associated_courses_ids': [8]},
#         ]
#     },
# }

# # --- دوال مساعدة (Helper Functions) ---
# def get_course_details(course_id):
#     """
#     تعيد اسم المقرر وكوده لمعرف مقرر معين.
#     """
#     for course in dummy_courses_for_dropdown:
#         if course['id'] == course_id:
#             return {'id': course['id'], 'name': f"{course['name']} ({course['code']})"}
#     return {'id': course_id, 'name': "مقرر غير معروف"}


# # دالة لوحة التحكم - لا يوجد تغيير هنا من الردود السابقة
# def dashboard_view(request):
#     """
#     تعرض لوحة التحكم الرئيسية بإحصائيات مجمعة.
#     """
#     total_departments = len(dummy_departments_data)
#     total_students = 0
#     total_teachers = 15 # قيمة وهمية
#     total_courses = len(dummy_courses_for_dropdown) # جميع المقررات المتاحة
#     total_levels = 0 # سيتم عد المستويات عبر جميع الأقسام

#     for dept_id, dept_data in dummy_departments_data.items():
#         total_students += sum(level['num_students'] for level in dept_data['levels_data'])
#         total_levels += len(dept_data['levels_data'])

#     stats = {
#         'total_students': total_students,
#         'total_teachers': total_teachers,
#         'total_departments': total_departments,
#         'total_levels': total_levels,
#         'total_courses': total_courses,
#     }

#     context = {
#         'page_title': 'لوحة التحكم الرئيسية',
#         'stats': stats,
#     }
#     return render(request, 'dashboard.html', context)


# # دالة إدارة الأقسام - لا يوجد تغيير هنا من الردود السابقة
# def departments_management_view(request):
#     """
#     تعرض صفحة إدارة الأقسام الرئيسية وقائمة بالأقسام.
#     تحسب الإحصائيات الديناميكية لكل قسم.
#     """
#     departments = list(dummy_departments_data.values())

#     overall_total_students = 0
#     overall_total_courses = 0

#     for dept in departments:
#         # حساب إجمالي الطلاب لهذا القسم بناءً على مستوياته
#         dept_total_students = sum(level['num_students'] for level in dept['levels_data'])
#         dept['total_students'] = dept_total_students
#         overall_total_students += dept_total_students

#         # حساب المقررات الفريدة التي يتم تدريسها عبر جميع المستويات في هذا القسم
#         dept_unique_courses_ids = set()
#         for level in dept['levels_data']:
#             dept_unique_courses_ids.update(level['associated_courses_ids'])
#         dept['num_courses'] = len(dept_unique_courses_ids) # هذا هو عدد المقررات الفريدة للقسم
#         overall_total_courses += dept['num_courses'] # مجموع المقررات الفريدة لكل قسم

#     stats = {
#         'total_departments': len(departments),
#         'overall_total_students': overall_total_students,
#         'overall_total_courses': overall_total_courses,
#     }

#     context = {
#         'page_title': 'إدارة التخصصات والأقسام',
#         'departments': departments,
#         'stats': stats,
#     }
#     return render(request, 'programs/list.html', context)

# # دالة إضافة/تعديل قسم - هذا هو الجزء الذي تم تحديثه
# def add_edit_department_view(request, pk=None):
#     """
#     تتولى إضافة قسم جديد أو تعديل قسم موجود.
#     تدير هذه الدالة تفاصيل القسم، وعدد الطلاب لكل مستوى،
#     والمقررات المرتبطة بكل مستوى.
#     """
#     department = None
#     if pk: # وضع التعديل
#         department = dummy_departments_data.get(pk)
#         if not department:
#             return redirect('departments_management')

#     if request.method == 'POST':
#         if pk: # تحديث قسم موجود
#             department_obj = dummy_departments_data[pk]
#             department_obj['name'] = request.POST.get('department_name')
#             department_obj['description'] = request.POST.get('description')
#             # 'num_levels' تُرك ثابتًا لتبسيط المثال، حيث أن إضافة/حذف المستويات ديناميكيًا
#             # مع بيانات وهمية يكون معقدًا ويتطلب منطقًا إضافيًا لإنشاء/حذف كيانات مستوى فعلية.

#             updated_levels_data = []
#             # المرور على المستويات الموجودة لتحديث بيانات الطلاب والمقررات
#             for level_data_old in department_obj['levels_data']:
#                 level_id = level_data_old['level_id']
                
#                 # جلب عدد الطلاب لهذا المستوى
#                 num_students = int(request.POST.get(f"level_{level_id}_students", 0))

#                 # جلب معرفات المقررات المرتبطة بهذا المستوى.
#                 # request.POST.getlist() يستخدم لأن المقررات تُرسل كمدخلات متعددة بنفس الاسم.
#                 associated_courses = [
#                     int(cid) for cid in request.POST.getlist(f"level_{level_id}_courses[]") if cid.isdigit()
#                 ]

#                 updated_levels_data.append({
#                     'level_id': level_id,
#                     'name': level_data_old['name'], # الاحتفاظ بالاسم الحالي للمستوى
#                     'num_students': num_students,
#                     'associated_courses_ids': associated_courses,
#                 })
            
#             department_obj['levels_data'] = updated_levels_data

#             # إعادة حساب إجمالي الطلاب للقسم
#             department_obj['total_students'] = sum(level['num_students'] for level in department_obj['levels_data'])
            
#             # إعادة حساب المقررات الفريدة للقسم
#             dept_unique_courses = set()
#             for level in department_obj['levels_data']:
#                 dept_unique_courses.update(level['associated_courses_ids'])
#             department_obj['num_courses'] = len(dept_unique_courses)

#         else: # إضافة قسم جديد (تبسيط شديد لغرض البيانات الوهمية)
#             new_id = max(dummy_departments_data.keys()) + 1 if dummy_departments_data else 1
#             new_department = {
#                 'id': new_id,
#                 'name': request.POST.get('department_name'),
#                 'description': request.POST.get('description'),
#                 'total_students': 0, # سيتم حسابها إذا تم إضافة مستويات
#                 'num_levels': 0, # مؤقت
#                 'num_courses': 0, # سيتم حسابها إذا تم إضافة مستويات ومقررات
#                 'levels_data': [], # يجب إضافة منطق لإنشاء مستويات افتراضية هنا بناءً على 'num_levels' إذا كان مدخلًا
#             }
#             dummy_departments_data[new_id] = new_department

#         return redirect('departments_management')

#     # لطلبات GET (عرض النموذج)
#     all_courses_for_dropdown = dummy_courses_for_dropdown
    
#     if department:
#         for level in department['levels_data']:
#             # إعداد تفاصيل المقررات الحالية في هذا المستوى لعرضها
#             current_courses_details = []
#             for course_id in level.get('associated_courses_ids', []):
#                 current_courses_details.append(get_course_details(course_id))
#             level['current_courses_details'] = current_courses_details

#     context = {
#         'page_title': 'إدارة القسم/التخصص',
#         'department': department,
#         'all_courses': all_courses_for_dropdown, # جميع المقررات المتاحة للإضافة
#     }
#     return render(request, 'programs/add_edit.html', context)

# # دالة حذف قسم - لا يوجد تغيير هنا من الردود السابقة
# def delete_department_view(request, pk):
#     """
#     تتولى حذف قسم (تُفعل بطلب POST من النافذة المنبثقة).
#     """
#     if request.method == 'POST':
#         if pk in dummy_departments_data:
#             del dummy_departments_data[pk]
#             print(f"تم حذف القسم ذو المعرف {pk} (وهمي).")
#         return redirect('departments_management')
#     # إذا وصل طلب GET هنا (مثلاً، وصول مباشر)، أعد التوجيه
#     return redirect('departments_management')



