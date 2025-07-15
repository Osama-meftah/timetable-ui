# import_students.py
import pandas as pd
from timetable.models import Teacher, Today, Period, TeacherTime,Subject,Program,Hall,Level,Group,Distribution

def import_from_availability_excel(file_path):
    df = pd.read_excel(file_path)
    teacher_times = []

    # خريطة الأعمدة إلى رقم الفترة
    time_columns = {
        'Time1': 1,
        'Time2': 2,
        'Time3': 3
    }

    for _, row in df.iterrows():
        professor_id = row['ProfessorID']
        day_id = row['Days']

        try:
            teacher = Teacher.objects.get(id=professor_id)
            today: Today = Today.objects.get(id=day_id)
        except (Teacher.DoesNotExist, Today.DoesNotExist) as e:
            print(f"❌ تخطي الصف بسبب خطأ في الأستاذ أو اليوم: {e}")
            continue

        for column, period_number in time_columns.items():
            if pd.notna(row[column]) and int(row[column]) == 1:
                try:
                    period = Period.objects.get(id=period_number)
                    teacher_times.append(TeacherTime(
                        fk_teacher=teacher,
                        fk_today=today,
                        fk_period=period
                    ))
                except Period.DoesNotExist:
                    print(f"⚠️ لم يتم العثور على فترة برقم {period_number}")

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
        id= row.get('CourseID')  # استخدام معرف المادة من الملف
        if subject_name:
            # تحقق إذا كانت المادة موجودة بنفس الاسم لتفادي التكرار (يمكن تغييره حسب المطلوب)
            if not Subject.objects.filter(subject_name=subject_name).exists():
                subject = Subject(
                    subject_name=subject_name,
                    id=id,  # استخدام معرف المادة من الملف
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
        
        if program_name:
            # تحقق إذا كان البرنامج موجود بنفس الاسم لتفادي التكرار (يمكن تغييره حسب المطلوب)
            if not Program.objects.filter(program_name=program_name).exists():
                program = Program(
                    program_name=program_name,
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


        if level_name and fk_program_id is not None:
            
            # تحقق إذا كان المستوى موجود بنفس الاسم لتفادي التكرار (يمكن تغييره حسب المطلوب)
            if not Level.objects.filter(level_name=level_name, fk_program=fk_program_id).exists():
                fk_program_id=Program.objects.get(id=fk_program_id)  # الحصول على الكائن البرنامج باستخدام المعرف
                # إنشاء الكائن المستوى
                level = Level(
                    level_name=level_name,
                    fk_program=fk_program_id,
                   
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

        if group_name and fk_level_id is not None:
            # تحقق إذا كانت المجموعة موجودة بنفس الاسم لتفادي التكرار (يمكن تغييره حسب المطلوب)
            if not Group.objects.filter(group_name=group_name, fk_level_id=fk_level_id).exists():
                fk_level_id = Level.objects.get(id=fk_level_id)
                group = Group(
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
            print(f"❌ المدرس غير موجود: ID = {row['ProfessorID']}")
        except Subject.DoesNotExist:
            print(f"❌ المادة غير موجودة: ID = {row['CourseID']}")
        except Group.DoesNotExist:
            print(f"❌ المجموعة غير موجودة: ID = {row['GroupID']}")
        except Exception as e:
            print(f"⚠️ خطأ غير متوقع في السطر {row}: {e}")

    print("✅ تم استيراد التوزيع بنجاح.")

# الاستخدام:
# import_from_availability_excel("../algorithm/data/ProDayTimes.xlsx")
# import_teachers_from_excel("../algorithm/data/Professors.xlsx")
# import_subjects_from_excel("../algorithm/data/Courses.xlsx")
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

# from .models import Teacher
for t in Teacher.objects.all():
    print(f"{t.id} - {t.teacher_status} - {t.get_teacher_status_display()}")
