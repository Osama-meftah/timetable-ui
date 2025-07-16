# import_students.py
import pandas as pd
from timetable.models import Teacher, Today, Period, TeacherTime,Subject,Program,Hall,Level,Group,Distribution,Department,Table
from django.apps import apps
def import_from_availability_excel(file_path):
    df = pd.read_excel(file_path)
    teacher_times = []

    # خريطة الأعمدة إلى رقم الفترة
    time_columns = {
        'Time1': 4,
        'Time2': 2,
        'Time3': 3
    }

    for _, row in df.iterrows():
        professor_id = row['ProfessorID']
        day_id = row['Days']+7

        try:
            teacher = Teacher.objects.get(id=professor_id)
            today: Today = Today.objects.get(id=day_id)
        except (Teacher.DoesNotExist, Today.DoesNotExist) as e:
            print(f"❌ skip row  {e} for ProfessorID: {professor_id}, Day ID: {day_id}")
            continue

        for column, period_number in time_columns.items():
            if pd.notna(row[column]) and int(row[column]) == 1:
                try:
                    period = Period.objects.get(id=period_number)
                    teacher_times.append(TeacherTime(
                        fk_teacher=teacher,
                        fk_today=today,
                        fk_period=period,
                    ))
                except Period.DoesNotExist:
                    print(f"⚠️ not find period {period_number}")

    TeacherTime.objects.bulk_create(teacher_times)
    print(f"✅ تم إدخال {len(teacher_times)} وقتًا بنجاح.")

def import_teachers_from_excel(file_path):
    df = pd.read_excel(file_path)

    for _, row in df.iterrows():
        teacher_name = row.get('ProfessorName')
        teacher_id = row.get('ProfessorID')
        
    
        if teacher_name:
            # تحقق إذا كان المدرس موجود بنفس الاسم لتفادي التكرار (يمكن تغييره حسب المطلوب)
            if not Teacher.objects.filter(teacher_name=teacher_name).exists():
                teacher = Teacher(
                    id=teacher_id,  # استخدام معرف المدرس من الملف
                    teacher_name=teacher_name,
                    # teacher_address='',       # لا يوجد في الملف
                    # teacher_phone='',         # لا يوجد في الملف
                    teacher_email=f"{teacher_name.replace(' ', '').lower()}@example.com",  # بريد وهمي
                     # افتراضياً نشط
                )
                teacher.save()
            else:
                print(f"Teacher '{teacher_name}' already exists, skipping.")
        else:
            print("Empty teacher name, skipping.")

    print("Import finished.")

def import_subjects_from_excel(file_path):
    df=pd.read_excel(file_path)
    for _, row in df.iterrows():
        subject_name= row.get('Subject')
        id= row.get('CourseID')
        term=row.get('term')  # استخدام معرف المادة من الملف
        if subject_name:
            # تحقق إذا كانت المادة موجودة بنفس الاسم لتفادي التكرار (يمكن تغييره حسب المطلوب)
            if not Subject.objects.filter(subject_name=subject_name).exists():
                subject = Subject(
                    subject_name=subject_name,
                    id=id,
                    term=term  # استخدام معرف المادة من الملف
                    # افتراضياً الفصل الأول
                )
                subject.save()
            else:
                print(f"Subject '{subject_name}' already exists, skipping.")

def import_day(file_path):
    df=pd.read_excel(file_path)
    for _,row in df.iterrows():
        day_name=row['Day Name']
        id=row['Day Number']
        
        day=Today(
            id=id,
            day_name=day_name
        )
        day.save()

def import_period(file_path):
    df=pd.read_excel(file_path)
    for _,row in df.iterrows():
        time_from=row['period_from']
        time_to=row['period_to']

        period=Period(
            period_from=int(time_from),
            period_to=int(time_to)
        )
        period.save()

def import_programs(file_path):
    df = pd.read_excel(file_path)
    for _, row in df.iterrows():
        program_name = row['name']
        fk_department_id = row['fk_dept']
        
        if program_name:
            # تحقق إذا كان البرنامج موجود بنفس الاسم لتفادي التكرار (يمكن تغييره حسب المطلوب)
            if not Program.objects.filter(program_name=program_name).exists():
                program = Program(
                    program_name=program_name,
                    fk_department=Department.objects.get(id=fk_department_id)
                )
                program.save()
            else:
                print(f"Program '{program_name}' already exists, skipping.")
        else:
            print("Empty program name, skipping.")

def import_halls_from_excel(file_path):
    df = pd.read_excel(file_path)
    for _, row in df.iterrows():
        hall_name = row['room_name']
        capacity_hall = row['capacity'] # افتراضياً نشط

        if hall_name:
            # تحقق إذا كانت القاعة موجودة بنفس الاسم لتفادي التكرار (يمكن تغييره حسب المطلوب)
            if not Hall.objects.filter(hall_name=hall_name).exists():
                hall = Hall(
                    hall_name=hall_name,
                    capacity_hall=capacity_hall,
                 
                )
                hall.save()
            else:
                print(f"Hall '{hall_name}' already exists, skipping.")
        else:
            print("Empty hall name, skipping.")

def import_levels_from_excel(file_path):
    df = pd.read_excel(file_path)
    for _, row in df.iterrows():
        level_name = row['name']
        fk_program_id = row['program_id']
        level_id = row['id']  # استخدام معرف المستوى من الملف


        if level_name and fk_program_id is not None:
            
            # تحقق إذا كان المستوى موجود بنفس الاسم لتفادي التكرار (يمكن تغييره حسب المطلوب)
            if not Level.objects.filter(level_name=level_name, fk_program=fk_program_id).exists():
                fk_program_id=Program.objects.get(id=fk_program_id)  # الحصول على الكائن البرنامج باستخدام المعرف
                # إنشاء الكائن المستوى
                level = Level(
                    id=level_id,  # استخدام معرف المستوى من الملف
                    level_name=level_name,
                    fk_program=fk_program_id,
                    number_students=300
                   
                )
                level.save()
            else:
                print(f"Level '{level_name}' already exists for program ID {fk_program_id}, skipping.")
        else:
            print("Empty level name or program ID, skipping.")

def import_groups_from_excel(file_path):
    df = pd.read_excel(file_path)
    for _, row in df.iterrows():
        group_name = row['name']
        fk_level_id = row['level_id']
        number_students = row['std_count']
        group_id = row['id']  # استخدام معرف المجموعة من الملف

        if group_name and fk_level_id is not None:
            # تحقق إذا كانت المجموعة موجودة بنفس الاسم لتفادي التكرار (يمكن تغييره حسب المطلوب)
            if not Group.objects.filter(group_name=group_name, fk_level_id=fk_level_id).exists():
                fk_level_id = Level.objects.get(id=fk_level_id)
                group = Group(
                    id=group_id,  # استخدام معرف المجموعة من الملف
                    group_name=group_name,
                    fk_level=fk_level_id,
                    number_students=number_students
                )
                group.save()
            else:
                print(f"Group '{group_name}' already exists for level ID {fk_level_id}, skipping.")
        else:
            print("Empty group name or level ID, skipping.")
def import_distributions(file_path):
    df = pd.read_excel(file_path)

    for _, row in df.iterrows():
        try:
            teacher = Teacher.objects.get(id=row['ProfessorID'])
            subject = Subject.objects.get(id=row['CourseID'])
            group = Group.objects.get(id=row['GroupID'])

            Distribution.objects.get_or_create(
                fk_teacher=teacher,
                fk_subject=subject,
                fk_group=group
            )
        except Teacher.DoesNotExist:
            print(f"❌ not found teacher: ID = {row['ProfessorID']}")
        except Subject.DoesNotExist:
            print(f"❌ not foun course: ID = {row['CourseID']}")
        except Group.DoesNotExist:
            print(f"❌not found group: ID = {row['GroupID']}")
        except Exception as e:
            print(f"⚠️ error {row}: {e}")

    print("✅ تم استيراد التوزيع بنجاح.")
def import_deptartments(file_path):
    df = pd.read_excel(file_path)
    for _, row in df.iterrows():
        dept_name = row['dept_name']
        if dept_name:
            # تحقق إذا كان القسم موجود بنفس الاسم لتفادي التكرار (يمكن تغييره حسب المطلوب)
            if not Department.objects.filter(name=dept_name).exists():
                department = Department(
                    name=dept_name,
                )
                department.save()
            else:
                print(f"Department '{dept_name}' already exists, skipping.")
        else:
            print("Empty department name, skipping.")
folder_path="C:/Users/abuba/Desktop/alogorithm timetable/-university-timetable-scheduler/data/"
def import_all_data():
    # import_teachers_from_excel(folder_path + "Professors.xlsx")
    # import_subjects_from_excel(folder_path + "Courses_with_terms.xlsx")
    # import_from_availability_excel(folder_path + "ProDayTimes (1).xlsx")
    # import_day(folder_path + "Days.xlsx")
    # import_period(folder_path + "period.xlsx")
    # import_deptartments(folder_path + "department.xlsx")
    # import_programs(folder_path + "programs.xlsx")
    # import_halls_from_excel(folder_path + "Rooms.xlsx")
    # import_levels_from_excel(folder_path + "levels.xlsx")
    # import_groups_from_excel(folder_path + "groups.xlsx")
    import_distributions(folder_path + "teaching_group - Copy.xlsx")
    # import_distributions(folder_path + "teaching_group.xlsx")


# الاستخدام:
# import_from_availability_excel("../algorithm/data/ProDayTimes.xlsx")
# import_teachers_from_excel(folder_path + "Professors.xlsx")
# import_subjects_from_excel( folder_path + "Courses_with_terms.xlsx")
# import_day("../algorithm/data/Days.xlsx")
# import_period("../algorithm/data/period.xlsx")
# import_programs("../algorithm/data/programs.xlsx")
# import_halls_from_excel("../algorithm/data/Rooms.xlsx")
# import_levels_from_excel("../algorithm/data/levels.xlsx")
# import_groups_from_excel("../algorithm/data/groups.xlsx")
# import_distributions("../algorithm/data/teaching_group.xlsx")
# Teacher.objects.all().delete()
# Subject.objects.all().delete()
# Today.objects.all().delete()
# Distribution.objects.all().delete()
# TeacherTime.objects.all().delete()
# Level.objects.all().delete()
# Group.objects.all().delete()
# for model in apps.get_models():
#     model.objects.all().delete()

Table.objects.all().delete()

# import_all_data()
# from .models import Teacher
# for t in Teacher.objects.all():
#     print(f"{t.id} - {t.teacher_status} - {t.get_teacher_status_display()}")
