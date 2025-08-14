from django.db import models
from django.core.validators import MinValueValidator
from math import ceil
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from datetime import datetime

# Create your models here.

class Department(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم القسم", unique=True,error_messages={
            'unique': "هذا القسم مسجل بالفعل."
        }) # تم إضافة unique=True)
    description = models.TextField(verbose_name="وصف القسم", blank=True, null=True)

    class Meta:
        verbose_name = "قسم"
        verbose_name_plural = "الأقسام"
        ordering = ['name']

    def __str__(self):
        return self.name
    
class Program(models.Model):
    program_name = models.CharField(max_length=50, verbose_name="اسم البرنامج")
    fk_department = models.ForeignKey(
        'Department',
        on_delete=models.CASCADE,
        related_name='programs',
        verbose_name="القسم التابع له"
    )
    class Meta:
        verbose_name = "برنامج"
        verbose_name_plural = "البرامج"
        ordering = ['program_name']
        # إضافة قيد التفرد: لا يمكن أن يتكرر اسم البرنامج ضمن نفس القسم
        unique_together = ('program_name', 'fk_department')

    def __str__(self):
        return self.program_name

class Hall(models.Model):
    STATUS_CHOICES = [
        ('available', 'متاحة'),
        ('under_maintenance', 'تحت الصيانة')
    ]
    hall_name = models.CharField(max_length=50, verbose_name="اسم القاعة", unique=True, error_messages={
            'unique': "هذه القاعة مسجلة بالفعل."
        }) # تم إضافة unique=True
    capacity_hall = models.IntegerField(verbose_name="سعة القاعة", validators=[MinValueValidator(1)]) # إضافة MinValueValidator
    hall_status = models.CharField(choices=STATUS_CHOICES, verbose_name="حالة القاعة", default='available',max_length=20) # تم تصحيح القيمة الافتراضية

    class Meta:
        verbose_name = "قاعة"
        verbose_name_plural = "القاعات"
        ordering = ['-capacity_hall']
        
    def __str__(self):
        return self.hall_name
    
class Level(models.Model):

    LEVEL_NAME_CHOICES = [
        ("first", "الأول"),
        ("second", "الثاني"),
        ("third", "الثالث"),
        ("fourth", "الرابع"),
    ]
    level_name = models.CharField(
        max_length=50,
        choices=LEVEL_NAME_CHOICES,
        verbose_name="اسم المستوى"
    )
    number_students = models.IntegerField(
        verbose_name="عدد الطلاب",
        validators=[MinValueValidator(0)]
    )
    fk_program = models.ForeignKey(
        'Program',
        on_delete=models.CASCADE,
        related_name='levels',
        verbose_name="البرنامج"
    )

    class Meta:
        verbose_name = "مستوى"
        verbose_name_plural = "المستويات"
        unique_together = ('level_name', 'fk_program')

    def __str__(self):
        return f"{self.level_name} ({self.fk_program.program_name})"

    def save(self, *args, **kwargs):
        from .models import Group, Hall  # استيراد داخلي لتجنب circular import
        is_new = self._state.adding
        super().save(*args, **kwargs)  # نحفظ أولاً

        # حذف المجموعات السابقة عند التعديل
        if not is_new:
            Group.objects.filter(fk_level=self).delete()

        def number_to_letters(n):
            result = ""
            while n >= 0:
                result = chr(n % 26 + 65) + result
                n = n // 26 - 1
            return result

        # الحصول على سعة أكبر قاعة
        largest_hall = Hall.objects.order_by('-capacity_hall').first()
        max_hall_capacity = largest_hall.capacity_hall if largest_hall else 0

        if max_hall_capacity == 0:
            Group.objects.create(
                group_name="Group A",
                number_students=self.number_students,
                fk_level=self
            )
            return

        if self.number_students == 0:
            Group.objects.create(
                group_name="Group A",
                number_students=0,
                fk_level=self
            )
            return

        if self.number_students <= max_hall_capacity:
            Group.objects.create(
                group_name="Group A",
                number_students=self.number_students,
                fk_level=self
            )
        else:
            num_groups = ceil(self.number_students / max_hall_capacity)
            remaining_students = self.number_students

            for i in range(int(num_groups)):
                group_letter = number_to_letters(i)
                current_group_students = min(remaining_students, max_hall_capacity)

                Group.objects.create(
                    group_name=f"Group {group_letter}",
                    number_students=current_group_students,
                    fk_level=self
                )
                remaining_students -= current_group_students

# المجموعة (Group)
class Group(models.Model):
    group_name = models.CharField(max_length=50, verbose_name="اسم المجموعة")
    number_students = models.IntegerField(verbose_name="عدد الطلاب", validators=[MinValueValidator(0)]) # إضافة MinValueValidator
    fk_level = models.ForeignKey(
        Level, 
        on_delete=models.CASCADE, 
        related_name='groups', 
        verbose_name="المستوى"
    )
    
    class Meta:
        verbose_name = "مجموعة"
        verbose_name_plural = "المجموعات"
        ordering = ['fk_level__id', 'group_name'] # ترتيب حسب المستوى ثم اسم المجموعة
        unique_together = ('group_name', 'fk_level')

    def __str__(self):
        return f"{self.group_name} ({self.fk_level.level_name})"
    
class Subject(models.Model):
    # استخدام id كمعرف رئيسي
    STATUS_CHOICES = [
        ('term1', 'الأول'),
        ('term2', 'الثاني')
    ]
    subject_name = models.CharField(max_length=100, verbose_name="اسم المادة",unique=True,error_messages={
            'unique': "هذه المادة مسجلة بالفعل."
        }) # تم إضافة unique=True)
    term = models.CharField(choices=STATUS_CHOICES, verbose_name="الفصل الدراسي", default='term1',max_length=10)
    # إضافة علاقة ForeignKey مع Level
    class Meta:
        verbose_name = "مادة"
        verbose_name_plural = "المواد"
        ordering = ['subject_name']
        
    def __str__(self):
        return f"{self.subject_name}"

    
# الدكتور (Teacher)
class Teacher(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE, null=True, blank=True)
    STATUS_CHOICES = [
        ('active', 'نشط'),
        ('vacation', 'إجازة')
    ]
    teacher_name = models.CharField(max_length=50, verbose_name="اسم المدرس",unique=True,error_messages={
            'unique': "هذا المدرس مسجل بالفعل."
        }) # تم إضافة unique=True)
    teacher_status = models.CharField(choices=STATUS_CHOICES, verbose_name="حالة المدرس",max_length=100,default='active') # تم تصحيح القيمة الافتراضية 
    class Meta:
        verbose_name = "المدرس"
        verbose_name_plural = "المدرسين"
        ordering = ['teacher_name']

    def __str__(self):
        return self.teacher_name

# اليوم
class Today(models.Model):
    DAY_CHOICES = [
        ('0', 'السبت'),
        ('1', 'الأحد'),
        ('2', 'الاثنين'),
        ('3', 'الثلاثاء'),
        ('4', 'الأربعاء'),
        ('5', 'الخميس'),

    ]
     # استخدام id كمعرف رئيسي
    day_name = models.CharField(choices=DAY_CHOICES,max_length=10, unique=True,error_messages={
            'unique': "هذه اليوم مسجلة بالفعل."
        }) # تم إضافة unique=True) # إضافة unique=True
    
    class Meta:
        verbose_name = "يوم"
        verbose_name_plural = "الأيام"
        # يمكن الترتيب حسب ID أو ترتيب مخصص للأيام، لكن مع choices يفضل الترتيب المخصص إذا أردت ترتيب أيام الأسبوع بشكل منطقي
        ordering = ['id'] 


    def __str__(self):
        return self.get_day_name_display() # استخدام get_FOO_display() لعرض الاسم الكامل

# الفترة (Period)

class Period(models.Model):
    period_from = models.CharField(verbose_name="من الساعة", help_text="مثال: 08:00",max_length=10) # استخدام max_length لتحديد طول الحقل
    period_to = models.CharField(verbose_name="إلى الساعة", help_text="مثال: 10:00",max_length=10) # استخدام max_length لتحديد طول الحقل

    class Meta:
        verbose_name = "فترة"
        verbose_name_plural = "الفترات"
        # Ensure that no two periods have the exact same start and end times
        unique_together = ('period_from', 'period_to')
        # ordering = ['period_from','period_to'] # Order by start time for logical flow

    def __str__(self):
        # Format times to 12-hour format with AM/PM
        # from_time = self.period_from.strftime('%I:%M %p') # %I for 12-hour, %p for AM/PM
        # to_time = self.period_to.strftime('%I:%M %p')
        return f"{self.period_from} - {self.period_to}"

class TeacherTime(models.Model):
    fk_today = models.ForeignKey(
        Today, 
        on_delete=models.CASCADE, 
        related_name='teacher_availability', 
        verbose_name="اليوم"
    )
    fk_period = models.ForeignKey(
        Period, 
        on_delete=models.CASCADE, 
        related_name='teacher_availability', 
        verbose_name="الفترة"
    )
    fk_teacher = models.ForeignKey(
        Teacher, 
        on_delete=models.CASCADE, 
        related_name='available_times', 
        verbose_name="الأستاذ"
    )
    
    class Meta:
        verbose_name = "وقت الأستاذ"
        verbose_name_plural = "أوقات الأساتذة"
        unique_together = ('fk_teacher', 'fk_today', 'fk_period')
        ordering = ['fk_teacher__teacher_name', 'fk_today__id', 'fk_period__period_from']

    def __str__(self):
        return f"{self.fk_teacher.teacher_name} - {self.fk_today.day_name}"

def current_year():
    return datetime.now().year
class Distribution(models.Model):
    fk_group = models.ForeignKey(
        Group, 
        on_delete=models.CASCADE, 
        related_name='distributions', 
        verbose_name="المجموعة"
    )
    fk_teacher = models.ForeignKey(
        Teacher, 
        on_delete=models.CASCADE, 
        related_name='distributions', 
        verbose_name="الأستاذ"
    )
    fk_subject = models.ForeignKey(
        Subject, 
        on_delete=models.CASCADE, 
        related_name='distributions', 
        verbose_name="المادة"
    )
    date = models.DateField(auto_now_add=True,blank=True,null=True) # إضافة حقل التاريخ
    year = models.PositiveIntegerField(editable=False,default=current_year) # حقل السنة، غير قابل للتعديل

    class Meta:
        verbose_name = "توزيع"
        verbose_name_plural = "التوزيعات"
        unique_together = ('fk_group', 'fk_subject','year') 
        ordering = ['fk_subject__subject_name']

    def __str__(self):
        return f"{self.fk_teacher.teacher_name} - {self.fk_subject.subject_name} {self.fk_group.fk_level.fk_program.program_name} {self.fk_group.fk_level.level_name} ({self.fk_group.group_name})"

# الجدول (Table)
class Table(models.Model):
    SEMESTER_CHOICES = [
        ('term1', 'الأول'),
        ('term2', 'الثاني')
    ]
    created_at = models.DateField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    table = models.FileField(max_length=100, upload_to="tables_file/", verbose_name="ملف الجدول")
    # إضافة حقل اسم للجدول ليكون أكثر وصفية
    name = models.CharField(max_length=100, verbose_name="اسم الجدول", blank=True, null=True)
    semester= models.CharField(
        choices=SEMESTER_CHOICES, 
        verbose_name="الفصل الدراسي", 
        default='term1', 
        max_length=10
    ) # تم تصحيح القيمة الافتراضية
    
    class Meta:
        verbose_name = "جدول"
        verbose_name_plural = "الجداول"
        ordering = ['-created_at'] # ترتيب حسب تاريخ الإنشاء تنازلياً

    def __str__(self):
        if self.name:
            return f"{self.name} (تاريخ: {self.created_at})"
        return f"جدول بتاريخ: {self.created_at}"

# محاضرة (Lecture)
class Lecture(models.Model):
    fk_hall = models.ForeignKey(
        Hall, 
        on_delete=models.CASCADE, 
        related_name='lectures', 
        verbose_name="القاعة"
    )
    fk_table = models.ForeignKey(
        Table, 
        on_delete=models.CASCADE, 
        related_name='lectures', 
        verbose_name="الجدول"
    )

    fk_day=models.ForeignKey(Today,on_delete=models.CASCADE,related_name='day_lectures',verbose_name="اليوم",default=1) # إضافة قيمة افتراضية
    fk_period=models.ForeignKey(Period,on_delete=models.CASCADE,related_name='period_lectures',verbose_name="الفترة",default=1) # إضافة قيمة افتراضية
    fk_distribution = models.ForeignKey(
        Distribution, 
        on_delete=models.CASCADE, 
        related_name='lectures', 
        verbose_name="التوزيع"
    )

    class Meta:
        verbose_name = "محاضرة"
        verbose_name_plural = "المحاضرات"
        # قيود التفرد لضمان عدم تداخل المحاضرات:
        # 1. لا يمكن أن تكون نفس القاعة مشغولة في نفس الوقت لنفس الجدول.
        # 2. لا يمكن أن تكون نفس المجموعة (عبر التوزيع) مجدولة في نفس الوقت لنفس الجدول.
        # unique_together = (
        #     ('fk_hall', 'fk_teachertime', 'fk_table'),
        #     ('fk_distribution', 'fk_teachertime', 'fk_table')
        # )
        # ordering = ['fk_table__created_at', 'fk_teachertime__fk_today__id', 'fk_teachertime__fk_period__id']


    def __str__(self):
        return f"محاضرة: {self.fk_distribution.fk_subject.subject_name} في {self.fk_hall.hall_name} - {self.fk_period.period_from}-{self.fk_period.period_to})"
