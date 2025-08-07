from django.shortcuts import render, redirect
from django.views import View
import requests
from django.contrib import messages
from .utils import *
from django.middleware.csrf import get_token
from collections import Counter
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken
from django.core.cache import cache


BASE_API_URL = "http://127.0.0.1:8001/api/"

def page_notfoun_view(reqest):
    return render(reqest,'notFoune.html')

def dashboard(request):
    """
    عرض لوحة التحكم.
    """
    # subjects = api_get(Endpoints.subjects)
    # teachers_data = api_get(Endpoints.teachers)
    # total_teacher = len(teachers_data)
    # total_courses = len(subjects)
    # listName=[ sub.get('subject_name') for sub in subjects]
    # distribution =api_get(Endpoints.distributions)
    # distributionList=[ dist.get("fk_teacher")  for dist in distribution ]
    
    # countSubTeacher=[]
    # for teacher in teachers_data:
        
    #     teacher_id = teacher["id"]
    #     count=0
    #     for d in distribution:
    #         if d["fk_teacher"]["id"] == teacher_id:
    #             count+=1
    #     if count > 2:
    #         countSubTeacher.append({
    #             "name":teacher["teacher_name"],
    #             "countSub":count,
    #             "countHour":2*count
    #         })
    # # sorted(countSubTeacher)
    # countSubTeacher.sort(key=lambda item: item['countSub'], reverse=True)
    # allNamesTeachers=[]
    # teacherNotSubject=[]
    # for teach in teachers_data:
    #     allNamesTeachers.append(teach["teacher_name"])
    #     if teach not in distributionList:
    #         teacherNotSubject.append({"key": teach['id'],"val":teach["teacher_name"]})
            
    # halls=api_get(Endpoints.halls,request)
    # notActivHall=[]
    # allNamesHalls=[]
    # for hal in halls:
    #     allNamesHalls.append(hal["hall_name"])
    #     if hal["hall_status"] == "under_maintenance":
    #         notActivHall.append({"key": hal["id"],"val":hal["hall_name"]})
    
    # levels=api_get(Endpoints.levels,request)
    # allNamesLevels=[]

    # for level in levels:
    #     allNamesLevels.append(level["level_name"]) 
    
    # lecuters=api_get(Endpoints.lectures,request)
    # taimeTable=[]
    # periods=api_get(Endpoints.periods,request)
    # todays=api_get(Endpoints.todays,request)
    # for lecuter in lecuters:
    #     period_id=lecuter['fk_period']
    #     for p in periods: 
    #         if p["id"] == period_id:   
    #             period= f"{p['period_from']} - {p['period_to']}"
    #     day_id=lecuter['fk_day']
    #     for d in todays: 
    #         if d["id"] == day_id:
    #             day=  d['day_name_display'] 
    #     taimeTable.append({
    #         "subject": lecuter["fk_distribution"]["fk_subject"]["subject_name"],
    #         "level": lecuter["fk_distribution"]["fk_group"]["fk_level"]["level_name"],
    #         "teacher": lecuter["fk_distribution"]["fk_teacher"]["teacher_name"],
    #         "hall": lecuter["fk_hall"]["hall_name"],
    #         "day": day,
    #         "period": period, 
    #     })
    
    # context={
    #     "total_teacher":total_teacher,
    #     "total_courses":total_courses,
    #     "listName":listName,
    #     "teacherNotSubject":teacherNotSubject,
    #     "notActivHall":notActivHall,
    #     "allNamesTeachers":allNamesTeachers,
    #     "allNamesHalls":allNamesHalls,
    #     "allNamesLevels":allNamesLevels,
    #     "countSubTeacher":countSubTeacher,
    #     "taimeTable":taimeTable
    #     }
    return render(request, 'dashboard.html')



class TeachersAvailableView(View):
    def get(self, request, id=None):
        user = get_user_id(request)
        teacher = user.get('teacher') if user else None
        availabilities = []
        if teacher:
            teacher_name = teacher.get('teacher_name')
            availabilities = api_search_items(Endpoints.searchteacherstimes, teacher_name, request=request) or []
            print("اسم المدرس:", teacher_name)
        else:
            print("لا يوجد مدرس مرتبط بالمستخدم")

        days = api_get(Endpoints.todays, request=request) or []
        periods = api_get(Endpoints.periods, request=request) or []

        if isinstance(availabilities, dict):
            availabilities = [availabilities]

        context = {
            "availabilities": availabilities,
            "days": days,
            "periods": periods,
            "page_title": "أوقات التواجد",
        }
        return render(request, 'teachers_management/list.html', context)

    def post(self, request, id=None):
        availability_id = request.POST.get("availability_id")
        day_id = request.POST.get("day")
        period_id = request.POST.get("period")

        user = get_user_id(request)
        teacher = user.get("teacher") if user else None
        teacher_id = teacher.get("id") if teacher else None

        if not teacher_id:
            messages.error(request, "❌ يجب تسجيل الدخول أولاً.")
            return redirect("teachers_availability")

        if not day_id or not period_id:
            messages.error(request, "❌ جميع الحقول مطلوبة.")
            return redirect("teachers_availability")

        time_data = {
            "fk_today_id": day_id,
            "fk_period_id": period_id,
            "fk_teacher": teacher_id,
        }

        # print(time_data)
        api_post(f"{Endpoints.teacher_times}", time_data, request=request, redirect_to='teachers_availability')

        return redirect("teachers_availability")


def teacher_dashboard_view(request):
    user=request.session.get('user')
    # print(user)
    # user=User.objects.get(id=user_id)
    return render(request, 'teachers_management/dashboard_teatcher.html', {'teacher': user})

class TeacherManagementView(View):
    def get(self, request, id=None):

        try:
            if id:
                return api_get(f"{Endpoints.teachers}{id}/", request=request, 
                               render_template="teachers/add_edit.html")
            elif "add" in request.GET:
                return render(request, "teachers/add_edit.html", {"page_title": "إضافة مدرس"})
            # page = request.GET.get("page")
            # if page:
            #     page = int(page)
            # else:
            #     page = 1
            # default_paginated_response = {'results': [], 'count': 0}
            # teachers_data = api_get(Endpoints.teachers, request=request) or default_paginated_response
            # teacher_times_data = api_get(Endpoints.teacher_times, request=request) or default_paginated_response
            # distribution_data = api_get(f"{Endpoints.distributions}?page={page}", request=request) or default_paginated_response
            # distributions_list, total_distributions, total_pages, next_url, prev_url, current_page = get_data_details(distribution_data)
            # # print(distributions_list)
            # current_page = get_current_page(prev_url) + 1 if prev_url else 1
            # teachers_list = teachers_data.get('results', [])
            # times_list = teacher_times_data.get('results', [])
            # # distributions_list = distributions_data.get('results', [])
            # distributions_by_teacher = {}
            # for d in distributions_list:
            #     teacher_id = d.get("fk_teacher", {}).get("id")
            #     if teacher_id:
            #         course_info = {
            #             "subject_name": d.get("fk_subject", {}).get("subject_name", "N/A"),
            #             "group": d.get("fk_group", {}).get("group_name", "N/A"),
            #             "level": d.get("fk_group", {}).get("fk_level", {}).get("level_name", "N/A"),
            #             "program": d.get("fk_group", {}).get("fk_level", {}).get("fk_program", {}).get("program_name", "N/A"),
            #         }
            #         distributions_by_teacher.setdefault(teacher_id, []).append(course_info)

            # times_by_teacher = {}
            
            # for t in times_list:
            #     teacher_id = t.get("fk_teacher") # في هذا النموذج، المعرّف مباشر
            #     if teacher_id:
            #         time_info = {
            #             "day": t.get("fk_today", {}).get("day_name_display", "N/A"),
            #             "period": f"{t.get('fk_period', {}).get('period_from', '')} - {t.get('fk_period', {}).get('period_to', '')}"
            #         }
            #         times_by_teacher.setdefault(teacher_id, []).append(time_info)            
            # teachers_with_data = []
            # for teacher in teachers_list:
            #     teacher_id = teacher.get("id")
                
            #     courses = distributions_by_teacher.get(teacher_id, [])
            #     times = times_by_teacher.get(teacher_id, [])
            #     if courses:
            #         teachers_with_data.append({
            #             "teacher": teacher,
            #             "courses": courses,
            #             "availability": times,
            #         })

            # total_teachers = teachers_data.get('count', 0)
            # active_teachers_on_page = len([t for t in teachers_list if t.get("teacher_status") == "active"])
            # on_leave_teachers_on_page = len([t for t in teachers_list if t.get("teacher_status") == "vacation"])

            # context = {
            #     "page_title": "إدارة المدرسين",
            #     # "teachers": teachers_data, # مرر كائن الترقيم الكامل إلى القالب
            #     "teachers_with_data": teachers_with_data, # هذه القائمة يجب ترقيمها بشكل منفصل إذا كانت كبيرة
            #     "total_teachers": total_teachers,
            #     "active_teachers": active_teachers_on_page, 
            #     "on_leave_teachers": on_leave_teachers_on_page,
            #     'next_url': next_url,
            #     'prev_url': prev_url,
            #     'total_pages': total_pages,
            #     "current_page": current_page,
            #     }
            # context['page_range'] = range(1, total_pages + 1)
            
            
            return render(request, "teachers/list.html")
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
            # "id": id,
            "teacher_name": request.POST.get("teacher_name", "").strip(),
            "teacher_phone": request.POST.get("teacher_phone", "").strip(),
            "teacher_email": request.POST.get("teacher_email", "").strip(),
            "teacher_address": request.POST.get("teacher_address", "").strip(),
            "teacher_status": request.POST.get("teacher_status", "").strip(),
        }

        try: 
            if id:
                api_put(f"{Endpoints.teachers}{id}/", teacher_data, request=request)
                         
                return redirect(request.path)
            
            elif form_type == "upload_teachers":
                result = handle_file_upload_generic(
                    request,
                    file_field_name='data_file',
                    endpoint_url=f"{BASE_API_URL}{Endpoints.teachersUpload}",
                    success_title="✅ تم رفع ملف المدرسين بنجاح.",
                    error_title="❌ فشل رفع ملف المدرسين",
                    redirect_to=request.path_info,timeout=1000,
                )
                return result or redirect(request.path_info)
            else:
                # إضافة باستخدام api_post مع إعادة توجيه بعد الإضافة
                response=api_post(Endpoints.teachers, teacher_data, request=request)
                # if response.get('teacher'):
                #     teachers.append(response['teacher'])
                #     cache.set(KeysCach.teachers_data, teachers, timeout=KeysCach.timeout)
                return redirect(request.path)

        except Exception as e:
            messages.error(request, f"❌ حدث خطأ أثناء حفظ بيانات المدرس: {str(e)}")
            return redirect("teachers_management")


# class TeacherDeleteView(View):
#     def post(self, request, id):
#         try:
#             api_delete(f"{Endpoints.teachers}{id}/", request=request)
#             return redirect("teachers_management")
#         except Exception as e:
#             handle_exception(request, "حدث خطأ أثناء حذف المدرس", e)
#         return redirect("teachers_management")

class TeacherAvailabilityAndCoursesView(View):
    def get(self, request, id=None):
        try:
            teachers = api_get(f"{Endpoints.teachers}?paginate=false", request=request) or []
            days = api_get(f"{Endpoints.todays}?paginate=false", request=request) or []
            periods = api_get(f"{Endpoints.periods}?paginate=false", request=request) or []
            subjects = api_get(f"{Endpoints.subjects}?paginate=false", request=request) or []
            levels = api_get(f"{Endpoints.levels}?paginate=false", request=request) or []
            programs = api_get(f"{Endpoints.programs}?paginate=false", request=request) or []
            groups = api_get(f"{Endpoints.groups}?paginate=false", request=request) or []

            teacher = None
            teacher_times = []
            teacher_distributions = []

            if id:
                # teacher = api_get(f"{Endpoints.teachers}{id}/?paginate=false", request=request)
                # all_times = api_get(f"{Endpoints.teacher_times}?paginate=false", request=request) or []
                # # teacher_times = [t for t in all_times if t["fk_teacher"]["id"] == int(id)]
                # teacher_times = [t for t in all_times if t["fk_teacher"] == int(id)]
                # all_distributions = api_get(f"{Endpoints.distributions}?paginate=false", request=request) or []
                # teacher_distributions = [d for d in all_distributions if d["fk_teacher"]["id"] == int(id)]
                response = api_get(f"{Endpoints.distributions}?teacherId={id}", request=request) or []
                teacher_distributions=response['results']
                teacher=teacher_distributions[0]['fk_teacher']
                teacher_times=teacher_distributions[0]['fk_teacher']['available_times']


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
        path = request.path  # يعيد: "/teacherswithcourses/add/"
        last_segment = path.strip('/').split('/')[-1]
        try:
            if form_type == "courses_form":
                for i in range(1, 100):
                    group_id = request.POST.get(f'dist_group_{i}')
                    subject_id = request.POST.get(f'dist_subject_{i}')
                    dist_id = request.POST.get(f'distribution_id_{i}')
                    
                    if group_id and subject_id:
                        dist_data = {
                            "fk_group_id": group_id,
                            "fk_teacher_id": teacher_id,
                            "fk_subject_id": subject_id,
                        }
                        try:
                            if dist_id:
                                api_put(f"{Endpoints.distributions}{dist_id}/", dist_data, request=request)
                            else:
                                api_post(Endpoints.distributions, dist_data, request=request)
                        except Exception as e:
                            handle_exception(request, f"فشل حفظ توزيع رقم {i}", e)
                
                # return redirect("add_edit_teacher_with_courses", id=teacher_id)
            
            elif form_type == "times_form":
                for i in range(1, 100):
                    day_id = request.POST.get(f'time_day_{i}')
                    period_id = request.POST.get(f'time_period_{i}')
                    availability_id = request.POST.get(f'availability_id_{i}')
                    
                    if day_id and period_id:
                        time_data = {
                            "fk_today_id": day_id,
                            "fk_period_id": period_id,
                            "fk_teacher": teacher_id,
                        }
                        # print(time_data)
                        try:
                            if availability_id:
                                api_put(f"{Endpoints.teacher_times}{availability_id}/", time_data, request=request)
                            else:
                                api_post(Endpoints.teacher_times, time_data, request=request)
                                messages.success(request, "تم حفظ الأوقات المتاحة بنجاح.")
                        except Exception as e:
                            handle_exception(request, f"فشل حفظ وقت رقم {i}", e)
                    else:
                        break
                
                # return redirect("add_edit_teacher_with_courses", id=teacher_id)
            
            elif form_type == "delete_distribution":
                dist_id = request.POST.get("item_id")
                # print(dist_id)
                if dist_id:
                    try:
                        api_delete(f"{Endpoints.distributions}{dist_id}/", request=request)
                        messages.success(request, "تم حذف توزيع المقرر بنجاح.")
                    except Exception as e:
                        handle_exception(request, "فشل في حذف توزيع المقرر", e)
                # return redirect("add_edit_teacher_with_courses", id=teacher_id)
            
            elif form_type == "delete_availability":
                availability_id = request.POST.get("item_id")
                # print(availability_id)
                if availability_id:
                    try:
                        api_delete(f"{Endpoints.teacher_times}{availability_id}/", request=request)
                        messages.success(request, "تم حذف وقت التوفر بنجاح.")
                    except Exception as e:
                        handle_exception(request, "فشل في حذف وقت التوفر", e)
            if last_segment == "add":
                return redirect("add_edit_teacher_with_courses")
            elif last_segment == "edit":
                return redirect("add_edit_teacher_with_courses", id=teacher_id)
            else:
                messages.error(request, "نوع النموذج غير معروف.")
                return redirect(request.path_info)

        except Exception as e:
            handle_exception(request, "حدث خطأ أثناء الحفظ", e)
            return redirect(request.path_info)

class CoursesListView(View):
    def get(self, request):
        term= request.GET.get("term")
        subjects = api_get(f"{Endpoints.subjects}", request=request) or []
        # = teachers_data.get('results', [])
        subjects = subjects.get('results', [])
        # subjects= get_or_cache(f"{KeysCach.subjects_data}?term={term}", Endpoints.subjects, request)
        total_courses = len(subjects)
        active_courses = sum(1 for c in subjects if c.get("active", True))
        full_courses = sum(1 for c in subjects if c.get("is_full", False))
        csrf_token = get_token(request)
        # subjects_paginated = paginate_queryset(subjects, request, "page_courses", "page_courses_size", 5)
        return render(request, "courses/list.html", {
            "courses": subjects,
            "page_title": "إدارة المقررات",
            "total_courses": total_courses,
            "active_courses": active_courses,
            "full_courses": full_courses,
            "csrf_token": csrf_token,
        })
    
    def post(self, request):
        if request.POST.get("form_type") == "upload_courses":
            return handle_file_upload(
                request,
                file_field_name='data_file',
                endpoint_url=f"{BASE_API_URL}{Endpoints.uploadSubjects}",
                success_title="✅ تم رفع ملف المقررات بنجاح.",
                error_title="❌ فشل رفع ملف المقررات",
                redirect_to="courses_management"
            )
        
        messages.error(request, "عملية غير صالحة.")
        return redirect("courses_management")
    
class CourseCreateView(View):
    def get(self, request):
        return render(request, "courses/add_edit.html", {"page_title": "إضافة مقرر"})

   
class CourseUpdateView(View):
    def get(self, request, id):
        subject = api_get(f"{Endpoints.subjects}{id}/", request=request)
        if not subject:
            return redirect("courses_management")
        return render(request, "courses/add_edit.html", {"subject": subject, "page_title": "تعديل"})
    
# class CourseDeleteView(View):
#     def post(self, request, id):
#         api_delete(f"{Endpoints.subjects}{id}/", request=request)
#         subjects = cache.get(KeysCach.subjects_data)
#         for i, subject in enumerate(subjects):
#             if str(subject['id']) == str(id):
#                 del subjects[i]
#                 cache.set(KeysCach.subjects_data, subjects, timeout=KeysCach.timeout)
#                 break
#         return redirect("courses_management")




class RoomsListView(View):
    def get(self, request):
        page = request.GET.get("page")
        if page:
            page = int(page)
        else:
            page = 1
        # print(page)
        rooms = api_get(f"{Endpoints.halls}?page={page}", request=request) or []
        rooms, total_rooms, total_pages, next_url, prev_url, current_page = get_data_details(rooms)
        current_page = get_current_page(prev_url) + 1 if prev_url else 1
        # print(current_page)
        # rooms, total_rooms, total_pages, next_url, prev_url = get_data_details(rooms)
        # current_page = get_current_page(prev_url) + 1 if prev_url else 1
        # total_rooms = total_rooms
        maintenance_rooms = sum(1 for room in rooms if room['hall_status'] == 'under_maintenance')
        largest_capacity_room = max(rooms, key=lambda r: r['capacity_hall'], default=None)

        capacity_list = [room['capacity_hall'] for room in rooms]
        capacity_counts = dict(Counter(capacity_list))
        stats = {
            'total_rooms': total_rooms,
            'maintenance_rooms': maintenance_rooms,
            'largest_capacity_room': largest_capacity_room,
            'capacity_counts': capacity_counts,
        }
        
        # room_paginated = rooms
        # paginate_queryset(rooms, request, "page", "page_size", 8)
        # next_url = f'{int(next_url) + 1}'
        context = {
            'page_title': 'إدارة القاعات',
            'rooms': rooms,
            'stats': stats,
            'next_url': next_url,
            'prev_url': prev_url,
            'total_pages': total_pages,
            "current_page": current_page,
        }
        context['page_range'] = range(1, total_pages + 1)
        return render(request, 'rooms/list.html', context)

    def post(self, request):
        # رفع ملف القاعات من نفس الصفحة
        return handle_file_upload(
            request,
            file_field_name='data_file',
            endpoint_url=f"{BASE_API_URL}{Endpoints.uploadHalls}",  # تأكد من صحة الرابط
            success_title="✅ تم رفع ملف القاعات بنجاح.",
            error_title="❌ فشل رفع ملف القاعات.",
            redirect_to="rooms_management"
        )

class RoomCreateView(View):
    def get(self, request):
        return render(request, 'rooms/add_edit.html', {"page_title": "إضافة قاعة"})

    def post(self, request):
        new_room_data = {
            "hall_name": request.POST.get("name"),
            "capacity_hall": int(request.POST.get("capacity")),
            "hall_status": request.POST.get("status"),
        }
        try:
            api_post(Endpoints.halls, new_room_data, request=request)
            # messages.success(request, "✅ تم إضافة القاعة بنجاح.")
        except RuntimeError as e:
            messages.error(request, f"❌ خطأ في إضافة القاعة: {e}")

        return render(request, 'rooms/add_edit.html', {
            "page_title": "إضافة قاعة",
        })
        
class RoomUpdateView(View):
    def get(self, request, id):
        room = api_get(f"{Endpoints.halls}{id}/", request=request)
        return render(request, 'rooms/add_edit.html', {"page_title": "تعديل قاعة", "room": room})

    def post(self, request, id):
        updated_data = {
            "hall_name": request.POST.get("name"),
            "capacity_hall": int(request.POST.get("capacity")),
            "hall_status": request.POST.get("status"),
        }
        try:
            api_put(f"{Endpoints.halls}{id}/", updated_data)
            messages.success(request, "✅ تم تحديث القاعة بنجاح.")
        except RuntimeError as e:
            messages.error(request, f"❌ خطأ في التحديث: {e}")

        return redirect('rooms_management')
class RoomDeleteView(View):
    def post(self, request, id):
        try:
            api_delete(f"{Endpoints.halls}{id}/", request=request)
            messages.success(request, "✅ تم حذف القاعة بنجاح.")
        except RuntimeError as e:
            messages.error(request, f"❌ فشل حذف القاعة: {e}")
        return redirect('rooms_management')

class DepartmentsListView(View):
    def get(self, request):
        try:
            dept = api_get(f"{Endpoints.departments}?paginate=false", request=request)
            programs = api_get(f"{Endpoints.programs}?paginate=false", request=request)
            levels = api_get(f"{Endpoints.levels}?paginate=false", request=request)

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

            context = {
                'page_title': 'إدارة التخصصات والأقسام',
                'departments': dept,
                'programs': programs_with_levels,
                'stats': stats,
            }
            return render(request, 'departments/list.html',context)
        except Exception as e:
            handle_exception(request, "فشل في جلب البيانات", e)
            messages.error(request, f"حدث خطأ أثناء تحميل الصفحة: {e}")
            return redirect('departments_management')

    def post(self, request):
        action = request.POST.get('form_type')

        if action == 'upload_departments':
            return handle_file_upload_generic(
                request,
                file_field_name='data_file',
                endpoint_url=f"{BASE_API_URL}{Endpoints.departmentsUpload}",
                success_title="✅ تم رفع ملف الأقسام بنجاح.",
                error_title="❌ فشل رفع ملف الأقسام",
                redirect_to='departments_management'
            )
        elif action == 'upload_programs':
            return handle_file_upload_generic(
                request,
                file_field_name='data_file',
                endpoint_url=f"{BASE_API_URL}{Endpoints.programsUpload}",
                success_title="✅ تم رفع ملف البرامج بنجاح.",
                error_title="❌ فشل رفع ملف البرامج",
                redirect_to='departments_management'
            )
        else:
            messages.error(request, "إجراء غير معروف.")
            return redirect('departments_management')
class DepartmentCreateView(View):
    def get(self, request):
        return render(request, 'departments/add_edit.html', {"page_title": "إضافة قسم"})

    def post(self, request):
        name = request.POST.get("department_name", "").strip()
        desc = request.POST.get("description", "").strip()

        if not name:
            messages.error(request, "اسم القسم مطلوب.")
            return redirect('add_department')

        try:
            new_dept_data = {"name": name, "description": desc}
            api_post(Endpoints.departments, new_dept_data)
            messages.success(request, "تم إضافة قسم بنجاح.")
        except RuntimeError as e:
            messages.error(request, f"خطأ في إضافة القسم: {e}")

        return redirect('departments_management')

class DepartmentUpdateView(View):
    def get(self, request, id):
        dept = api_get(f"{Endpoints.departments}{id}/")
        return render(request, 'departments/add_edit.html', {"department": dept, "page_title": "تعديل قسم"})

    def post(self, request, id):
        name = request.POST.get("department_name", "").strip()
        desc = request.POST.get("description", "").strip()

        if not name:
            messages.error(request, "اسم القسم مطلوب.")
            return redirect('edit_department', id=id)

        try:
            updated_dept_data = {"name": name, "description": desc}
            api_put(f"{Endpoints.departments}{id}/", updated_dept_data)
            messages.success(request, "تم تحديث بيانات القسم بنجاح.")
        except RuntimeError as e:
            messages.error(request, f"خطأ في تحديث القسم: {e}")

        return redirect('departments_management')

class DepartmentDeleteView(View):
    def post(self, request, id):
        try:
            api_delete(f"{Endpoints.departments}{id}/")
            messages.success(request, "تم حذف القسم بنجاح.")
        except RuntimeError as e:
            messages.error(request, f"خطأ في حذف القسم: {e}")
        return redirect('departments_management')

class AddProgramLevelView(View):
    def get(self, request):
        programs = api_get(f"{Endpoints.programs}?paginate=false",request)
        levels = api_get(f"{Endpoints.levels}?paginate=false",request)
        # print(levels)
        departments = api_get(f"{Endpoints.departments}?paginate=false",request)
        # print(departments)
        # print(programs)
        return render(request, 'programs/add_edit.html', {
            "programs": programs,
            "levels": levels,
            "departments": departments,
            "page_title": "إضافة"
        })

    def post(self, request):
        form_type = request.POST.get('form_type')
        types = request.POST.get('type')
        # if form_type == "program_form_submit":
        #     program_name = request.POST.get('program_name')
        #     fk_department_id = request.POST.get('fk_department')
        #     data = {
        #         'program_name': program_name,
        #         'department_id': fk_department_id,
        #     }
        #     try:
        #         api_post(Endpoints.programs, data)
        #         messages.success(request, "✅ تم إضافة البرنامج بنجاح!")
        #     except Exception as e:
        #         handle_exception(request, f"❌ فشل حفظ البرنامج {data}", e)

        # if form_type == "level_form_submit":
        #     level_id = request.POST.get('level_id')
        #     level_name = request.POST.get('level_name')
        #     number_students = request.POST.get('number_students')
        #     fk_program_id = request.POST.get('fk_program')
        #     # print(fk_program_id)
        #     if types =='add':
        #         level_data = {
        #             "level_name": level_name,
        #             "number_students": number_students,
        #             "program_name": fk_program_id
        #         }
        #         print(level_data)
        #         # print()
        #         try:
        #             api_post(Endpoints.levels, level_data)
        #         except Exception as e:
        #             handle_exception(request, f"❌ فشل حفظ المستوى {level_data}", e)
        #     else:
        #         level_data = {
        #             "level_name": level_name,
        #             "number_students": number_students,
        #             "program_name": fk_program_id
        #             }
        #         print(level_data)
        #         try:
        #             api_put(f"{Endpoints.levels}{level_id}/", level_data)
        #             messages.success(request, "✅ تم تعديل المستوى بنجاح!")
        #         except Exception as e:
        #             handle_exception(request, f"❌ فشل تعديل المستوى {level_data}", e)

        if form_type == 'upload_levels':
            handle_file_upload_generic(
                request,
                file_field_name='data_file',
                endpoint_url=f"{BASE_API_URL}{Endpoints.levelsUpload}",
                success_title="✅ تم رفع ملف المستويات بنجاح.",
                error_title="❌ فشل رفع ملف المستويات"
            )

        return redirect(request.path_info)
class EditProgramLevelView(View):
    def get(self, request, id):
        program = api_get(f"{Endpoints.programs}{id}/")
        programs = api_get(f"{Endpoints.programs}?paginate=false",request)
        levels = api_get(f"{Endpoints.levels}?paginate=false",request)
        departments = api_get(f"{Endpoints.departments}?paginate=false",request)
        # programs = api_get(Endpoints.programs)
        # print(levels)
        # levels = api_get(Endpoints.levels)
        # departments = api_get(Endpoints.departments)
        # print(departments)
        return render(request, 'programs/add_edit.html', {
            "program": program,
            "programs": programs,
            "levels": levels,
            "departments": departments,
            "page_title": "تعديل"
        })

    def post(self, request, id):
        form_type = request.POST.get('form_type')
        if form_type == 'upload_levels':
            handle_file_upload_generic(
                request,
                file_field_name='data_file',
                endpoint_url=f"{BASE_API_URL}{Endpoints.levelsUpload}",
                success_title="✅ تم رفع ملف المستويات بنجاح.",
                error_title="❌ فشل رفع ملف المستويات"
            )

        return redirect(request.path_info)
    #     types = request.POST.get('type')
        # print(types)
        # if form_type == "program_form_submit":
        #     program_name = request.POST.get('program_name')
        #     fk_department_id = request.POST.get('fk_department')
        #     data = {
        #         'program_name': program_name,
        #         'department_id': fk_department_id,
        #     }
            
        #     try:
        #         api_put(f"{Endpoints.programs}{id}/", data)
        #         # messages.success(request, "✅ تم تعديل البرنامج بنجاح!")
        #     except Exception as e:
        #         handle_exception(request, f"❌ فشل تعديل البرنامج {data}", e)

        # if form_type == "level_form_submit":
        #     level_id = request.POST.get('level_id')
        #     level_name = request.POST.get('level_name')
        #     number_students = request.POST.get('number_students')
        #     fk_program_id = request.POST.get('fk_program')

        #     if types =='add':
        #         level_data = {
        #             "level_name": level_name,
        #             "number_students": number_students,
        #             "program_name": fk_program_id
        #         }
        #         # print("level_data", level_data)
        #         try:
        #             api_post(Endpoints.levels, level_data,request)
        #             # messages.success(request, "✅ تم إضافة المستوى بنجاح!")
        #         except Exception as e:
        #             handle_exception(request, f"❌ فشل حفظ المستوى {level_data}", e)
        #     else:
        #         level_data = {
        #             "level_name": level_name,
        #             "number_students": number_students,
        #             "program_name": fk_program_id
        #             }
        #         try:
        #             api_put(f"{Endpoints.levels}{level_id}/", level_data,request)
        #             # messages.success(request, "✅ تم تعديل المستوى بنجاح!")
        #         except Exception as e:
        #             handle_exception(request, f"❌ فشل تعديل المستوى {level_data}", e)

        # return redirect(request.path_info)
class DeleteProgramLevelView(View):
    def post(self, request,id=None):
        item_id = request.POST.get('item_id')
        item_type = request.POST.get('selected_level_or_program')

        try:
            if item_type == 'program':
                api_delete(f"{Endpoints.programs}{item_id}/")
                messages.success(request, "✅ تم حذف البرنامج بنجاح.")
            elif item_type == 'level':
                api_delete(f"{Endpoints.levels}{item_id}/")
                messages.success(request, "✅ تم حذف المستوى بنجاح.")
            else:
                messages.error(request, "❌ نوع العنصر غير معروف.")
        except Exception as e:
            messages.error(request, f"❌ حدث خطأ أثناء الحذف: {e}")
            # print(f"Error deleting item {item_type} with ID {item_id}: {e}")

        return redirect('add_program')


class TimeTableSettingsView(View):
    def get(self, request, id=None):
        if request.session.get('conflicts'):
            available_unscheduled=request.session.get('available_unscheduled')
            conflicts= request.session.get('conflicts')
        else:
            conflicts = []
            available_unscheduled=[]


        return render(request, 'timetables/list.html',{'conflicts': conflicts,'available_unscheduled':available_unscheduled})
    
    
class PeriodsView(View):
    def get(self, request, id=None):
        return render(request, 'periods/period_management.html')

class GroupsView(View):
    def get(self, request, id=None):
        response = api_get(Endpoints.programs, request=request)
        if response['results']:
            programs=response['results']
        else:
            programs=[]
        print(programs)
        return render(request, 'groups/list.html', { "page_title": "إدارة المجموعات","program":programs})

    def post(self, request):
        # استقبال بيانات الإضافة أو التعديل من المودال (فورم)
        action_type = request.POST.get('form_type')  # add أو edit
        group_id = request.POST.get('group_id')  # موجود فقط عند التعديل
        # موجود فقط عند التعديل
        data = {
            "group_name": request.POST.get("group_name"),
            "number_students": request.POST.get("number_students"),
            "fk_level_id": request.POST.get("fk_level"),
        }
        # print(data)
        try:
            if action_type == 'add':
                api_post(Endpoints.groups, data, request=request, success_message="✅ تم إضافة المجموعة بنجاح.", redirect_to='groups_management')
                # messages.success(request, "✅ تم إضافة المجموعة بنجاح.")
            elif action_type == 'edit' and group_id:
                api_put(f"{Endpoints.groups}{group_id}/", data, request=request, redirect_to='groups_management')
                # messages.success(request, "✅ تم تعديل المجموعة بنجاح.")
            else:
                messages.error(request, "نوع العملية غير صحيح أو بيانات ناقصة.")
        except Exception as e:
            messages.error(request, f"❌ حدث خطأ: {e}")
        return redirect('groups_management')


class GroupDeleteView(View):
    def post(self, request,id=None):
        item_id = request.POST.get('item_id')
        try:
            api_delete(f"{Endpoints.groups}{item_id}/", request=request, redirect_to='groups_management')
            # messages.success(request, "✅ تم حذف المجموعة بنجاح.")
        except Exception as e:
            messages.error(request, f"❌ حدث خطأ أثناء حذف المجموعة: {e}")
            # print(f"Error deleting group with ID {item_id}: {e}")

        return redirect('groups_management')
    

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



