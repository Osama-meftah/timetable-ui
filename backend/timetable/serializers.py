from rest_framework import serializers
from .models import (
    Program, Hall, Level, Group, Subject, Teacher,
    Today, Period, TeacherTime, Distribution, Table, Lecture,Department
)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db.models import Sum
from django.contrib.auth.models import User, Permission
# في ملف serializers.py

from django.contrib.auth.models import User
from rest_framework import serializers

# ... (باقي الـ Serializers لديك مثل UserCreateSerializer)

# class UserRoleSerializer(serializers.ModelSerializer):
#     """
#     Serializer مخصص لجلب وتحديث حقل is_staff فقط.
#     """
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'is_staff']
#         read_only_fields = ['id', 'username']

# class UserCreateSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True) # كلمة المرور للكتابة فقط

#     class Meta:
#         model = User
#         fields = ['id', 'username', 'email', 'password']
    
#     def create(self, validated_data):
#         # نستخدم create_user لضمان تجزئة كلمة المرور بشكل صحيح
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             email=validated_data['email'],
#             password=validated_data['password']
#         )
#         return user

# class PermissionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Permission
#         fields = ['id', 'name','codename']
        
        
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'description']
        
        

class ProgramSerializer(serializers.ModelSerializer):
    # عرض القسم كمعلومة فقط (قراءة)
    fk_department = DepartmentSerializer(read_only=True)

    # دعم إدخال القسم إما بالمعرف أو الاسم
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), write_only=True, required=False, source='fk_department'
    )
    department_name = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Program
        fields = ['id', 'program_name', 'fk_department', 'department_id', 'department_name']

    def validate(self, data):
        # نحاول ربط fk_department إما بالـ ID أو بالاسم
        dept_id = data.get('fk_department', None)
        dept_name = data.pop('department_name', None)

        if not dept_id and dept_name:
            department = Department.objects.filter(name__iexact=dept_name.strip()).first()
            if not department:
                raise serializers.ValidationError({"department_name": f"القسم '{dept_name}' غير موجود."})
            data['fk_department'] = department

        if not data.get('fk_department'):
            raise serializers.ValidationError("يجب تحديد القسم إما بـ department_id أو department_name.")

        return data

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class HallSerializer(serializers.ModelSerializer):
    hall_status_display = serializers.CharField(source='get_hall_status_display', read_only=True)
    class Meta:
        model = Hall
        fields = '__all__'
        
class LevelSerializer(serializers.ModelSerializer):
    fk_program = ProgramSerializer(read_only=True)
    program_name = serializers.CharField(write_only=True)  # استلام اسم البرنامج بدلاً من المعرف
    level_name_display= serializers.CharField(source='get_level_name_display', read_only=True)

    class Meta:
        model = Level
        fields = ['id', 'level_name', 'number_students', 'fk_program', 'program_name', 'level_name_display']

    def create(self, validated_data):
        program_name = validated_data.pop('program_name', None)
        if program_name:
            program = Program.objects.filter(program_name__iexact=program_name.strip()).first()
            if not program:
                raise serializers.ValidationError({'program_name': f"البرنامج '{program_name}' غير موجود."})
            validated_data['fk_program'] = program
        return super().create(validated_data)

    def update(self, instance, validated_data):
        program_name = validated_data.pop('program_name', None)
        if program_name:
            program = Program.objects.filter(program_name__iexact=program_name.strip()).first()
            if not program:
                raise serializers.ValidationError({'program_name': f"البرنامج '{program_name}' غير موجود."})
            validated_data['fk_program'] = program
        return super().update(instance, validated_data)




class GroupSerializer(serializers.ModelSerializer):
    fk_level = LevelSerializer(read_only=True)
    fk_level_id = serializers.PrimaryKeyRelatedField(
        queryset=Level.objects.all(),
        write_only=True,
        source='fk_level'
    )

    class Meta:
        model = Group
        fields = ['id', 'group_name', 'number_students', 'fk_level', 'fk_level_id']

    def validate(self, data):
        group_name = data.get('group_name')
        level = data.get('fk_level')
        number_students = data.get('number_students')

        # الحصول على السجل الحالي إذا كان موجود (عند التحديث)
        instance = getattr(self, 'instance', None)

        # تحقق من تكرار اسم المجموعة لنفس المستوى
        queryset = Group.objects.filter(group_name=group_name, fk_level=level)
        if instance:
            queryset = queryset.exclude(pk=instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("هذه المجموعة موجودة مسبقًا لهذا المستوى.")

        # حساب مجموع عدد الطلاب في المجموعات الأخرى لنفس المستوى
        other_groups = Group.objects.filter(fk_level=level)
        if instance:
            other_groups = other_groups.exclude(pk=instance.pk)
        total_students_other_groups = other_groups.aggregate(total=Sum('number_students'))['total'] or 0

        # مجموع الطلاب بعد إضافة/تعديل هذه المجموعة
        total_students_after = total_students_other_groups + number_students

        # مقارنة مع عدد طلاب المستوى
        if total_students_after > level.number_students:
            raise serializers.ValidationError(
                f"مجموع عدد طلاب المجموعات ({total_students_after}) أكبر من عدد طلاب المستوى ({level.number_students})."
            )

        return data



class SubjectSerializer(serializers.ModelSerializer):
    # fk_level = LevelSerializer(read_only=True)
    # fk_level_id = serializers.PrimaryKeyRelatedField(
    #     queryset=Level.objects.all(), source='fk_level', write_only=True
    # )

    class Meta:
        model = Subject
        fields = ['id', 'subject_name', 'term']
class TeacherBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['id','teacher_name','teacher_status']

class UserSerializer(serializers.ModelSerializer):
    teacher = TeacherBriefSerializer(read_only=True)
    # username= serializers.CharField(source='username', read_only=True)# اسم الحقل لازم يطابق اسم العلاقة في الموديل
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff','is_superuser', 'teacher']
        
class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email','is_staff','is_superuser']
class TodaySerializer(serializers.ModelSerializer):
    day_name_display = serializers.CharField(source='get_day_name_display', read_only=True)
    class Meta:
        model = Today
        fields = ['id', 'day_name', 'day_name_display']

class PeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Period
        fields = ['id', 'period_from', 'period_to']
    
class TeacherTimeSerializer2(serializers.ModelSerializer):
    fk_today = TodaySerializer(read_only=True)
    fk_period = PeriodSerializer(read_only=True)
    fk_today_id = serializers.PrimaryKeyRelatedField(
        queryset=Today.objects.all(), source='fk_today', write_only=True
    )
    fk_period_id = serializers.PrimaryKeyRelatedField(
        queryset=Period.objects.all(), source='fk_period', write_only=True
    )

    class Meta:
        model = TeacherTime
        fields = '__all__'

class TeacherSerializer(serializers.ModelSerializer):
    teacher_status_display = serializers.CharField(source='get_teacher_status_display', read_only=True)
    user = UserBriefSerializer(read_only=True)
    class Meta:
        model = Teacher
        fields = ['id', 'teacher_name', 'teacher_status','teacher_status_display','user']

class TeacherSerializer2(serializers.ModelSerializer):
    teacher_status_display = serializers.CharField(source='get_teacher_status_display', read_only=True)
    available_times = TeacherTimeSerializer2(many=True, read_only=True)
    class Meta:
        model = Teacher
        fields = ['id', 'teacher_name', 'teacher_status','teacher_status_display','available_times']

class TeacherTimeSerializer(serializers.ModelSerializer):
    # للقراءة
    fk_today = TodaySerializer(read_only=True)
    fk_period = PeriodSerializer(read_only=True)
    # fk_teacher = TeacherSerializer(read_only=True)

    # للكتابة
    fk_today_id = serializers.PrimaryKeyRelatedField(
        queryset=Today.objects.all(), source='fk_today', write_only=True
    )
    fk_period_id = serializers.PrimaryKeyRelatedField(
        queryset=Period.objects.all(), source='fk_period', write_only=True
    )
    fk_teacher = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all())

    class Meta:
        model = TeacherTime
        fields = '__all__'

    def validate(self, data):
        fk_today = data.get('fk_today_id')
        fk_period = data.get('fk_period_id')
        fk_teacher = data.get('fk_teacher_id')

        qs = TeacherTime.objects.filter(
            fk_today=fk_today,
            fk_period=fk_period,
            fk_teacher=fk_teacher
        )
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError("هذا الوقت موجود مسبقًا لنفس المدرس في نفس اليوم.")

        return data

    def create(self, validated_data):
        instance = super().create(validated_data)
        self.success_message = "تم إنشاء وقت الأستاذ بنجاح."
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        self.success_message = "تم تحديث وقت الأستاذ بنجاح."
        return instance
# Serializer للنموذج Distribution
class DistributionSerializer(serializers.ModelSerializer):
    fk_group = GroupSerializer(read_only=True)
    fk_teacher = TeacherSerializer2(read_only=True)
    fk_subject = SubjectSerializer(read_only=True)

    fk_group_id = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), source='fk_group', write_only=True
    )
    fk_teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all(), source='fk_teacher', write_only=True
    )
    fk_subject_id = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(), source='fk_subject', write_only=True
    )

    class Meta:
        model = Distribution
        fields = '__all__'


class TableSerializer(serializers.ModelSerializer):
    semester_display = serializers.CharField(source='get_semester_display', read_only=True)
    class Meta:
        model = Table
        fields = ['id', 'name', 'table', 'semester', 'semester_display', 'created_at']

# Serializer للنموذج Lecture
class LectureSerializer(serializers.ModelSerializer):
    fk_hall = HallSerializer(read_only=True) # عرض بيانات القاعة
    fk_table = TableSerializer(read_only=True) # عرض بيانات الجدول
    fk_teachertime = TeacherTimeSerializer(read_only=True) # عرض بيانات وقت الأستاذ
    fk_distribution = DistributionSerializer(read_only=True) # عرض بيانات التوزيع
    fk_day = TodaySerializer(read_only=True) # عرض بيانات اليوم
    fk_period = PeriodSerializer(read_only=True) # عرض بيانات الفترة

    class Meta:
        model = Lecture
        fields = '__all__'


class TeacherCourseInfoSerializer(serializers.Serializer):
    subject_name = serializers.CharField()
    group = serializers.CharField()
    level = serializers.CharField()
    program = serializers.CharField()

class AvailabilityInfoSerializer(serializers.Serializer):
    day = serializers.CharField()
    period = serializers.CharField()

class TeacherWithDetailsSerializer(serializers.Serializer):
    teacher = TeacherSerializer()
    courses = TeacherCourseInfoSerializer(many=True)
    availability = AvailabilityInfoSerializer(many=True)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # teacher=Teacher.objects.get(user=user)
        # أضف بيانات مخصصة هنا
        # token['is_staff']=user.is_staff
        # token['is_superuser']=user.is_superuser
        # token['teacher_username']=user.username
        # token['teacher_email']=teacher.teacher_email
        # token['id']=teacher.pk
        # token['user_id']=user.pk
        return token
    

