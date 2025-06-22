from django.shortcuts import render,redirect, get_object_or_404

# Create your views here.

def login(request):
    return render(request, 'login.html')

def dashboard(request):
    return render(request, 'dashboard.html')


dummy_teacher_data = {
    1: {'id': 1, 'name': 'أ. أحمد السيد (وهمي)', 'email': 'ahmed.dummy@example.com', 'phone': '0501111111'},
    2: {'id': 2, 'name': 'أ. فاطمة الزهراء (وهمي)', 'email': 'fatima.dummy@example.com', 'phone': '0552222222'},
}

# --- دوال عرض المدرسين (Views) المبسطة ---

def add_edit_teacher_view(request, pk=None):
    """
    تعرض صفحة إضافة مدرس جديد أو تعديل مدرس موجود.
    لا تقوم بعمليات حفظ أو تحديث فعلية.
    """
    teacher = None
    if pk: # إذا تم توفير pk، فهذا يعني أننا في وضع التعديل
        # هنا، نستخدم بيانات وهمية فقط للعرض في القالب
        # في تطبيق حقيقي، ستستجلب بيانات المدرس من قاعدة البيانات
        teacher = dummy_teacher_data.get(pk)
        if not teacher:
            # إذا لم يتم العثور على مدرس بالمعرف، يمكن إعادة التوجيه
            return redirect('teachers_management')

    if request.method == 'POST':
        # في هذا السيناريو المبسط، لا نقوم بأي معالجة لبيانات POST
        # فقط نعيد التوجيه لإظهار أن "العملية تمت"
        print(f"تم استقبال بيانات POST لـ {'التعديل' if pk else 'الإضافة'}: {request.POST}")
        return redirect('teachers_management') # إعادة التوجيه بعد "العملية"

    context = {
        'page_title': 'إدارة المدرس',
        'teacher': teacher # تمرير كائن المدرس (إذا كان وضع التعديل) إلى القالب
    }
    return render(request, 'teachers/add_edit.html', context)

def confirm_delete_teacher_view(request, pk):
    """
    تعرض صفحة تأكيد حذف مدرس.
    لا تقوم بعملية حذف فعلية.
    """
    teacher = dummy_teacher_data.get(pk) # جلب بيانات وهمية للعرض
    if not teacher:
        return redirect('teachers_management')

    if request.method == 'POST':
        # في هذا السيناريو المبسط، لا نقوم بأي عملية حذف فعلية
        print(f"تم تأكيد طلب حذف المدرس ID: {pk}")
        return redirect('teachers_management') # إعادة التوجيه بعد "الحذف"

    context = {
        'page_title': 'تأكيد حذف المدرس',
        'teacher': teacher # تمرير كائن المدرس إلى القالب للتأكيد
    }
    return render(request, 'teachers/confirm_delete_teacher.html', context)


def teachers_with_courses_list_view(request):
    # بيانات المدرسين الأصلية (التي تحافظ على جميع الحقول المطلوبة في الجدول التفصيلي)
    teachers = [
        {
            'id': 1,
            'name': 'أ. أحمد السيد',
            'email': 'ahmed@example.com', # البريد الإلكتروني موجود هنا الآن
            'phone': '0501234567',
            'image_url': 'https://via.placeholder.com/40x40/4F46E5/FFFFFF?text=AS',
            'status': 'نشط',
            'courses': 'رياضيات، فيزياء',
            'availability': [
                {'day': 'الأحد', 'times': '08:00 - 12:00'},
                {'day': 'الثلاثاء', 'times': '10:00 - 14:00'},
            ],
        },
        {
            'id': 2,
            'name': 'أ. فاطمة الزهراء',
            'email': 'fatima@example.com', # البريد الإلكتروني موجود هنا الآن
            'phone': '0557654321',
            'image_url': 'https://via.placeholder.com/40x40/EC4899/FFFFFF?text=FZ',
            'status': 'إجازة',
            'courses': 'لغة عربية، تربية إسلامية',
            'availability': [],
        },
        {
            'id': 3,
            'name': 'أ. خالد العنزي',
            'email': 'khalid@example.com', # البريد الإلكتروني موجود هنا الآن
            'phone': '0569876543',
            'image_url': 'https://via.placeholder.com/40x40/22C55E/FFFFFF?text=KC',
            'status': 'نشط',
            'courses': 'علوم، كيمياء',
            'availability': [
                {'day': 'الإثنين', 'times': '09:00 - 13:00'},
                {'day': 'الأربعاء', 'times': '14:00 - 18:00'},
            ],
        },
    ]

    # إنشاء قائمة المدرسين المبسطة من قائمة المدرسين الأصلية
    # هذا يضمن أن البيانات "القديمة" (الكاملة) هي المصدر
    simplified_teachers = [
        {'id': t['id'], 'name': t['name'], 'phone': t['phone'], 'email': t['email']}
        for t in teachers
    ]

    # بيانات تقارير المدرسين
    total_teachers = len(teachers)
    active_teachers = sum(1 for t in teachers if t['status'] == 'نشط')
    on_leave_teachers = sum(1 for t in teachers if t['status'] == 'إجازة')

    context = {
        'page_title': 'إدارة المدرسين',
        'teachers': teachers, # للجدول التفصيلي
        'simplified_teachers': simplified_teachers, # للجدول المبسط الجديد والمشتق من teachers
        'total_teachers': total_teachers,
        'active_teachers': active_teachers,
        'on_leave_teachers': on_leave_teachers,
    }
    return render(request, 'teachers/teacher_management.html', context)

def teacher_with_courses_form_view(request, pk=None):
    teacher = None
    if pk:
        page_title = 'تعديل بيانات المدرس'
        teacher = {
            'id': pk,
            'name': 'أحمد السيد', 'email': 'ahmed@example.com', 'phone': '0501234567',
            'image_url': 'https://via.placeholder.com/100x100/4F46E5/FFFFFF?text=AS',
            'status': 'نشط', 'courses': 'رياضيات، فيزياء', 'notes': 'مدرس ممتاز ولديه خبرة 5 سنوات.',
            'availability': [{'day': 'الأحد', 'times': '08:00 - 12:00'}, {'day': 'الثلاثاء', 'times': '10:00 - 14:00'}],
        }
    else:
        page_title = 'إضافة مدرس جديد'
        teacher = {
            'id': None, 'name': '', 'email': '', 'phone': '', 'image_url': '',
            'status': 'نشط', 'courses': '', 'notes': '', 'availability': [],
        }
    
    if request.method == 'POST':
        teacher_name = request.POST.get('name')
        print(f"تم حفظ {'تعديلات' if pk else 'إضافة'} المدرس (ID: {pk if pk else 'جديد'}): {teacher_name}")
        return redirect('teachers_list')
    
    days_of_week = ['الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت']
    context = {'page_title': page_title, 'teacher': teacher, 'days_of_week': days_of_week}
    return render(request, 'teachers/add_edit_teacher_with_courses.html', context)

def delete_teacher_with_courses_view(request, pk):
    if request.method == 'POST':
        print(f"تم حذف المدرس ذو الـ ID: {pk}")
        return redirect('teachers_management')
    
    context = {
        'page_title': 'تأكيد حذف المدرس',
        'teacher': {'id': pk, 'name': f'المدرس ذو الـ ID: {pk}'}
    }
    return render(request, 'teachers/confirm_delete_teacher_with_courses.html', context)


def courses_list_view(request):
    # بيانات وهمية معدلة لعرض id و name فقط
    courses = [
        {'id': 1, 'name': 'رياضيات متقدمة'},
        {'id': 2, 'name': 'اللغة العربية: النحو'},
        {'id': 3, 'name': 'مبادئ البرمجة'},
        {'id': 4, 'name': 'الكيمياء العضوية'},
        {'id': 5, 'name': 'التربية الفنية'},
    ]

    context = {
        'courses': courses,
        'page_title': 'إدارة المقررات',
    }
    return render(request, 'courses/list.html', context)

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

# --- دوال العرض (View Functions) ---
# احتفظ بالدوال الأخرى الموجودة لديك مثل dashboard_view, timetable_settings_view إلخ
# (لن ندرجها هنا لتجنب التكرار)

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