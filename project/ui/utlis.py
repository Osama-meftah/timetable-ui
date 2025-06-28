import requests
from django.contrib import messages

BASE_API_URL = "http://127.0.0.1:8001/api/"

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
        'num_levels': 4,
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

dummy_teachers = [
    {'id': 1, 'name': 'أ.د. أحمد علي', 'specialty': 'علوم الحاسب', 'available_days_times': [{'day': 'الأحد', 'start': '08:00', 'end': '12:00'}, {'day': 'الثلاثاء', 'start': '10:00', 'end': '14:00'}]},
    {'id': 2, 'name': 'د. فاطمة الزهراء', 'specialty': 'الرياضيات', 'available_days_times': [{'day': 'الإثنين', 'start': '09:00', 'end': '13:00'}, {'day': 'الأربعاء', 'start': '11:00', 'end': '15:00'}]},
    {'id': 3, 'name': 'م. خالد محمود', 'specialty': 'هندسة البرمجيات', 'available_days_times': [{'day': 'الأحد', 'start': '13:00', 'end': '17:00'}, {'day': 'الخميس', 'start': '08:00', 'end': '12:00'}]},
    {'id': 4, 'name': 'أ. نورا سالم', 'specialty': 'اللغة الإنجليزية', 'available_days_times': [{'day': 'الإثنين', 'start': '08:00', 'end': '12:00'}, {'day': 'الثلاثاء', 'start': '09:00', 'end': '13:00'}]},
]

dummy_rooms = [
    {'id': 1, 'name': 'قاعة 101', 'capacity': 50, 'type': 'محاضرة'},
    {'id': 2, 'name': 'معمل حاسوب 1', 'capacity': 30, 'type': 'معمل'},
    {'id': 3, 'name': 'قاعة 205', 'capacity': 70, 'type': 'محاضرة'},
    {'id': 4, 'name': 'قاعة متعددة الأغراض', 'capacity': 100, 'type': 'محاضرة'},
]

# دالة مساعدة لجمع كل المستويات من الأقسام (يمكن أن تكون هنا أو في views.py حسب الحاجة)
def get_all_levels():
    all_levels = []
    for dept_id, dept_data in dummy_departments_data.items():
        for level in dept_data['levels_data']:
            all_levels.append({
                'id': level['level_id'],
                'name': level['name'],
                'department_name': dept_data['name']
            })
    return all_levels

# بيانات وهمية لحصة لتعديلها (في وضع التعديل)
dummy_session_for_edit = {
    'course_id': 3,  # مقدمة في البرمجة
    'teacher_id': 1, # أ.د. أحمد علي
    'room_id': 2,    # معمل حاسوب 1
    'level_id': 101, # المستوى الأول (CS)
    'day_of_week': 'الأحد',
    'start_time': '09:00',
    'end_time': '10:30',
}