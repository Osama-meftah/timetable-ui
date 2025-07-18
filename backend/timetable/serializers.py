from rest_framework import serializers
from .models import (
    Program, Hall, Level, Group, Subject, Teacher,
    Today, Period, TeacherTime, Distribution, Table, Lecture,Department
)


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'description']
        
        
?# class ProgramSerializer(serializers.ModelSerializer):
#     fk_department = DepartmentSerializer(read_only=True) 
#     department_id = serializers.PrimaryKeyRelatedField(
#         queryset=Department.objects.all(), write_only=True, source='fk_department'
#     )

#     class Meta:
#         model = Program
#         fields = ['id', 'program_name', 'fk_department', 'department_id']
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
    class Meta:
        model = Hall
        fields = '__all__'
        

# Serializer للنموذج Level
# class LevelSerializer(serializers.ModelSerializer):
#     fk_program = ProgramSerializer(read_only=True)  # للعرض
#     fk_program_id = serializers.PrimaryKeyRelatedField(
#         queryset=Program.objects.all(), write_only=True, source='fk_program'
#     )

#     class Meta:
#         model = Level
#         fields = '__all__'
class LevelSerializer(serializers.ModelSerializer):
    fk_program = ProgramSerializer(read_only=True)
    program_name = serializers.CharField(write_only=True)  # استلام اسم البرنامج بدلاً من المعرف

    class Meta:
        model = Level
        fields = '__all__'

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



# Serializer للنموذج Group
class GroupSerializer(serializers.ModelSerializer):
    fk_level = LevelSerializer(read_only=True) # عرض بيانات المستوى بدلاً من ID فقط

    class Meta:
        model = Group
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    # fk_level = LevelSerializer(read_only=True)
    # fk_level_id = serializers.PrimaryKeyRelatedField(
    #     queryset=Level.objects.all(), source='fk_level', write_only=True
    # )

    class Meta:
        model = Subject
        fields = ['id', 'subject_name', 'term']


class TeacherSerializer(serializers.ModelSerializer):
    teacher_status_display = serializers.CharField(source='get_teacher_status_display', read_only=True)
    class Meta:
        model = Teacher
        fields = ['id', 'teacher_name', 'teacher_phone', 'teacher_email', 'teacher_status','teacher_status_display', 'teacher_address']


class TodaySerializer(serializers.ModelSerializer):
    day_name_display = serializers.CharField(source='get_day_name_display', read_only=True)

    class Meta:
        model = Today
        fields = ['id', 'day_name', 'day_name_display']

class PeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Period
        fields = ['id', 'period_from', 'period_to']

class TeacherTimeSerializer(serializers.ModelSerializer):
    # للقراءة
    fk_today = TodaySerializer(read_only=True)
    fk_period = PeriodSerializer(read_only=True)
    fk_teacher = TeacherSerializer(read_only=True)

    # للكتابة
    fk_today_id = serializers.PrimaryKeyRelatedField(
        queryset=Today.objects.all(), source='fk_today', write_only=True
    )
    fk_period_id = serializers.PrimaryKeyRelatedField(
        queryset=Period.objects.all(), source='fk_period', write_only=True
    )
    fk_teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all(), source='fk_teacher', write_only=True
    )

    class Meta:
        model = TeacherTime
        fields = '__all__'

# Serializer للنموذج Distribution
class DistributionSerializer(serializers.ModelSerializer):
    # عرض بيانات المجموعة، الأستاذ، المادة (للقراءة فقط)
    fk_group = GroupSerializer(read_only=True)
    fk_teacher = TeacherSerializer(read_only=True)
    fk_subject = SubjectSerializer(read_only=True)

    # لإدخال البيانات (كتابة) تستخدم الحقول بالـ ID
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
    class Meta:
        model = Table
        fields = '__all__'

# Serializer للنموذج Lecture
class LectureSerializer(serializers.ModelSerializer):
    fk_hall = HallSerializer(read_only=True) # عرض بيانات القاعة
    fk_table = TableSerializer(read_only=True) # عرض بيانات الجدول
    fk_teachertime = TeacherTimeSerializer(read_only=True) # عرض بيانات وقت الأستاذ
    fk_distribution = DistributionSerializer(read_only=True) # عرض بيانات التوزيع

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
