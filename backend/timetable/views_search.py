# teachers/views.py
from collections import defaultdict
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from rest_framework.decorators import api_view
# لم تعد بحاجة إلى from django.shortcuts import render في هذا الـ view

class SearchTeacherAPIView(APIView):
    def get(self, request):
        query = request.GET.get("q", "").strip()
        try:
            teachers = Teacher.objects.all()
            if query:
                teachers = teachers.filter(teacher_name__icontains=query)

            serializer = TeacherSerializer(teachers, many=True)
            return Response({"results": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "message": "حدث خطأ أثناء تنفيذ البحث.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SearchTeacherTimeAPIView(APIView):
    def get(self, request):
        query = request.GET.get("q", "").strip().lower()

        teacher_times = TeacherTime.objects.select_related("fk_teacher", "fk_today", "fk_period")

        if query:
            teacher_times = teacher_times.filter(Q(fk_teacher__teacher_name__icontains=query))

        result = {}
        for t in teacher_times:
            teacher = t.fk_teacher
            teacher_id = teacher.id

            if teacher_id not in result:
                serialized_teacher = TeacherSerializer(teacher).data
                result[teacher_id] = {
                    "teacher": serialized_teacher,
                    "availability": []
                }

            result[teacher_id]["availability"].append({
                "day": TodaySerializer(t.fk_today).data,
                "period": PeriodSerializer(t.fk_period).data
            })

        return Response({"results": list(result.values())}, status=status.HTTP_200_OK)




class SearchTeacherDistributionAPIView(APIView):
    def get(self, request):
        query = request.GET.get("q", "").strip().lower()
        teachers = Teacher.objects.all()
        if query:
            teachers = teachers.filter(
                Q(teacher_name__icontains=query) 
            )

        distributions = Distribution.objects.select_related(
            "fk_teacher", "fk_subject", "fk_group__fk_level__fk_program"
        ).all()

        teacher_times = TeacherTime.objects.select_related(
            "fk_teacher", "fk_today", "fk_period"
        ).all()

        result = []

        for teacher in teachers:
            teacher_id = teacher.id

            # استخراج المقررات
            courses = []
            for d in distributions:
                if d.fk_teacher.id == teacher_id:
                    courses.append({
                        "subject_name": d.fk_subject.subject_name,
                        "group": d.fk_group.group_name,
                        "level": d.fk_group.fk_level.level_name,
                        "program": d.fk_group.fk_level.fk_program.program_name,
                    })

            # استخراج التوفر الزمني
            availability = []
            print(teacher_times)
            for t in teacher_times:
                if t.fk_teacher.id == teacher_id:
                    availability.append({
                        "day": t.fk_today.get_day_name_display(),
                        "period": f"{t.fk_period.period_from} - {t.fk_period.period_to}"
                    })

            if courses:
                result.append({
                    "teacher": teacher,
                    "courses": courses,
                    "availability": availability
                })

        serializer = TeacherWithDetailsSerializer(result, many=True)
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)


class SearchCoursesAPIView(APIView):
    def get(self, request):
        query = request.GET.get("q", "").strip().lower()
        courses = Subject.objects.all()
        if query:
            courses = courses.filter(subject_name__icontains=query)
        serializer = SubjectSerializer(courses, many=True)
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)


class SearchHallsAPIView(APIView):
    def get(self, request):
        query = request.GET.get("q", "").strip().lower()
        halls = Hall.objects.all()
        if query:
            halls = halls.filter(hall_name__icontains=query)
        serializer = HallSerializer(halls, many=True)
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)



@api_view(['GET'])
def Dashboard(request):
    # --- الخطوة 1: جلب كل البيانات من الـ API دفعة واحدة ---
    
    subjects = list(Subject.objects.all().values())
    teachers_data = list(Teacher.objects.all().values())
    distribution = list(Distribution.objects.all().values())
    halls = list(Hall.objects.all().values())
    levels = list(Level.objects.all().values())
    lecuters = list(Lecture.objects.all().values())
    periods = list(Period.objects.all().values())
    todays = list(Today.objects.all().values())
    programs = list(Program.objects.all().values())
    groups = list(Group.objects.all().values())
    table= list(Table.objects.all().values())

    # --- الخطوة 2: الفهرسة - تحويل القوائم إلى قواميس للبحث السريع (O(1)) ---
    
    # فهرسة المواد والمدرسين والقاعات لسهولة الوصول
    subjects_map = {s['id']: s for s in subjects}
    teachers_map = {t['id']: t for t in teachers_data}
    halls_map = {h['id']: h for h in halls}
    periods_map = {p['id']: f"{p['period_from']} - {p['period_to']}" for p in periods}
    todays_map = {d['id']: d['day_name'] for d in todays}
    levels_map = {l['id']: l for l in levels}
    groups_map = {g['id']: g for g in groups}
    programs_map = {p['id']: p for p in programs}
   
    # تجميع توزيع المواد حسب المدرس لتجنب الحلقات المتداخلة لاحقًا
    distributions_by_teacher = defaultdict(list)
    distributions_by_group = defaultdict(list)
    distributions_by_subject = defaultdict(list)
    allNamesTeachers=set()
    allNamesLevels=set()
    allNamesSubject=set()
    for dist in distribution:
        teacher_id = dist["fk_teacher_id"]
        group_id = dist["fk_group_id"]
        subject_id = dist["fk_subject_id"]
        allNamesSubject.add(subjects_map[dist["fk_subject_id"]]["subject_name"])
        allNamesTeachers.add(teachers_map[ dist["fk_teacher_id"]]["teacher_name"])
        allNamesLevels.add(f'{levels_map[groups_map[ dist["fk_group_id"]]["fk_level_id"]]["level_name"]} {programs_map[ levels_map[groups_map[ dist["fk_group_id"]]["fk_level_id"]]["fk_program_id"]]["program_name"]}')
        distributions_by_teacher[teacher_id].append(dist)
        distributions_by_group[group_id].append(dist)
        distributions_by_subject[subject_id].append(1)
   
    # --- الخطوة 3: معالجة البيانات باستخدام القواميس المُفهرسة ---
    subjectDeactivate = []
    if len(distributions_by_subject) is not len(subjects_map):
        print("______________")
        for sub_id,sub in subjects_map.items():
            subCount=len(distributions_by_subject[sub_id])
            if subCount==0:
                subjectDeactivate.append({
                    "key":sub_id,
                    "val":sub["subject_name"]
                })
                
    # حساب عدد المواد لكل مدرس وتحديد المدرسين غير المسند إليهم مواد
    countSubTeacher = []
    teacherNotSubject = []
    for teacher_id, teacher in teachers_map.items():
        assigned_subjects_count = len(distributions_by_teacher[teacher_id])
        # if assigned_subjects_count > 2:
        if assigned_subjects_count > 2:
            countSubTeacher.append({
                "name": teacher["teacher_name"],
                "countSub": assigned_subjects_count,
                "countHour": 2 * assigned_subjects_count
            })
        else:
            teacherNotSubject.append({"key": teacher_id, "val": teacher["teacher_name"]})
    
    countSubTeacher.sort(key=lambda item: item['countSub'], reverse=True)

    # تحديد القاعات غير النشطة
    notActivHall = [{"key": h_id, "val": hall["hall_name"]} for h_id, hall in halls_map.items() if hall["hall_status"] == "under_maintenance"]
    
    # إعداد الجدول الدراسي وحساب إشغال القاعات في حلقة واحدة
    taimeTable = []
    hall_occupancy = defaultdict(int) # لحساب عدد المحاضرات في كل قاعة
    table_id=table[len(table)-1]["id"]
    # table_id==lecuter["fk_table_id"]
    # allNamesHalls=[]
    allNamesHalls=set()
    for lecuter in lecuters:
        # print(lecuter["fk_table"]["id"])
        
        allNamesHalls.add(halls_map[ lecuter["fk_hall_id"]]["hall_name"])
        if table_id==lecuter["fk_table_id"]:
            dist_info = distribution[ lecuter["fk_distribution_id"]]
            group_info = groups_map.get(dist_info["fk_group_id"], {})
            level_info = levels_map.get(group_info.get("fk_level_id", {}), {})
            program_info = programs_map.get(level_info.get("fk_program_id", {}), {})
            
            taimeTable.append({
                "subject": subjects_map.get(dist_info["fk_subject_id"], {}).get("subject_name", "N/A"),
                "level": f'{level_info.get("level_name", "")} {program_info.get("program_name", "")}',
                "group":group_info["group_name"],
                "teacher": teachers_map.get(dist_info["fk_teacher_id"], {}).get("teacher_name", "N/A"),
                "hall": halls_map.get(lecuter["fk_hall_id"], {}).get("hall_name", "N/A"),
                "day": todays_map.get(lecuter['fk_day_id'], "N/A"),
                "period": periods_map.get(lecuter['fk_period_id'], "N/A"), 
            })
            hall_occupancy[lecuter["fk_hall_id"]] += 1

    # حساب نسبة إشغال القاعات
    busyWeekday = len(periods) * 6 # 6 أيام عمل
    busyHallList = []
    for hall_id, count in hall_occupancy.items():
        hall_name = halls_map.get(hall_id, {}).get("hall_name")
        capacity_hall = halls_map.get(hall_id, {}).get("capacity_hall")
        if hall_name:
            percentage = (count / busyWeekday) * 100 if busyWeekday > 0 else 0
            busyHallList.append({'hallName': hall_name, 'hallBusy': int(percentage),"capacityHall":capacity_hall})
            
    # حساب معلومات المستويات والمجموعات لكل برنامج
    levelSubjectInfo = []
    total_table_activ = 0
    total_studant=0
    for program in programs:
        levelInfo = []
        groupInfo = []
        program_levels = [level for level in levels if level["fk_program_id"] == program["id"]]
        for level in program_levels:
            level_groups = [group for group in groups if group["fk_level_id"] == level["id"]]
            group_count = len(level_groups)
            groupInfo.append(group_count)
            total_table_activ += group_count
            total_studant=level['number_students']
            
            subject_count = 0
            if level_groups:
                # حساب عدد المواد للمجموعة الأولى في المستوى (بافتراض أن كل المجموعات لها نفس المواد)
                subject_count = len(distributions_by_group.get(level_groups[0]["id"], []))
                
            levelInfo.append({"levelName": level["level_name"], "countSubjet": subject_count,"total_studant":total_studant})

        levelSubjectInfo.append({
            "program": program["program_name"],
            "levelInfo": levelInfo,
            "groupInfo": groupInfo
        })

    # --- الخطوة 4: تجميع البيانات النهائية للعرض ---
    context = {
        "total_teacher": len(teachers_data),
        "total_courses": len(subjects),
        "hall_available": f'{len(halls)}/{len(halls) - len(notActivHall)}',
        "total_table_activ": total_table_activ,
        "listName": allNamesSubject , # [s['subject_name'] for s in subjects],
        "subjectDeactivate":subjectDeactivate, 
    
        "teacherNotSubject": teacherNotSubject,
        # "teacherNotSubject": [],
      
        "notActivHall": notActivHall,
        # "notActivHall": [],
        "allNamesTeachers": allNamesTeachers, #   [t['teacher_name'] for t in teachers_data],
        "allNamesHalls": allNamesHalls , # [h['hall_name'] for h in halls],
        "allNamesLevels": allNamesLevels,#  [f'{lvl["level_name"]} {lvl["fk_program"]["program_name"]}' for lvl in levels],
        "countSubTeacher": countSubTeacher,
        "taimeTable": taimeTable,
        "busyHallList": busyHallList,
        "levelSubjectInfo": levelSubjectInfo
    }
    return Response(context)
