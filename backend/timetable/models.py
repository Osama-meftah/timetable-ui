from django.db import models

# Create your models here.

class Department(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم القسم", unique=True)
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

    def __str__(self):
        return self.program_name

# القاعة
class Hall(models.Model):
    STATUS_CHOICES = [
        ('متاحة', 'متاحة'),
        ('تحت الصيانة', 'تحت الصيانة') # Changed 'اجازة' to 'إجازة' for full word
    ]
    hall_name = models.CharField(max_length=50, verbose_name="اسم القاعة")
    capacity_hall = models.IntegerField(verbose_name="سعة القاعة")
    hall_status = models.CharField(choices=STATUS_CHOICES,verbose_name="حالة القاعة",default='متاح')
    class Meta:
        verbose_name = "قاعة"
        verbose_name_plural = "القاعات"
        ordering = ['hall_name']

    def __str__(self):
        return self.hall_name
    
    
class Level(models.Model):
    level_name = models.CharField(max_length=50, verbose_name="اسم المستوى")
    number_students = models.IntegerField(verbose_name="عدد الطلاب")
    fk_program = models.ForeignKey(
        Program, 
        on_delete=models.CASCADE, 
        related_name='levels', 
        verbose_name="البرنامج"
    )
    
    class Meta:
        verbose_name = "مستوى"
        verbose_name_plural = "المستويات"
        ordering = ['fk_program__program_name', 'level_name'] # ترتيب حسب البرنامج ثم المستوى

    def __str__(self):
        return f"{self.level_name} ({self.fk_program.program_name})"
    

# المجموعة (Group)
class Group(models.Model):
    group_name = models.CharField(max_length=50, verbose_name="اسم المجموعة")
    number_students = models.IntegerField(verbose_name="عدد الطلاب")
    fk_level = models.ForeignKey(
        Level, 
        on_delete=models.CASCADE, 
        related_name='groups', 
        verbose_name="المستوى"
    )
    
    class Meta:
        verbose_name = "مجموعة"
        verbose_name_plural = "المجموعات"
        ordering = ['fk_level__level_name', 'group_name'] # ترتيب حسب المستوى ثم اسم المجموعة

    def __str__(self):
        return f"{self.group_name} ({self.fk_level.level_name})"
 
class Subject(models.Model):
    subject_name = models.CharField(max_length=100, verbose_name="اسم المادة")
    term = models.CharField(max_length=50, verbose_name="الفصل الدراسي",default="الاول")
    fk_level = models.ForeignKey(
        Level, 
        on_delete=models.CASCADE, 
        related_name='subjects', 
        verbose_name="المستوى"
    )

    class Meta:
        verbose_name = "مادة"
        verbose_name_plural = "المواد"
        ordering = ['fk_level__level_name', 'subject_name']

    def __str__(self):
        # تم تصحيح اسم الحقل من self.name إلى self.subject_name
        return f"{self.subject_name} ({self.fk_level.level_name})"

    
# الدكتور (Teacher)
class Teacher(models.Model):
    STATUS_CHOICES = [
        ('نشط', 'نشط'),
        ('إجازة', 'إجازة') # Changed 'اجازة' to 'إجازة' for full word
    ]
    teacher_name = models.CharField(max_length=50, verbose_name="اسم المدرس")
    teacher_address = models.CharField(max_length=100, verbose_name="عنوان المدرس", blank=True, null=True)
    teacher_phone = models.CharField(max_length=15, verbose_name="هاتف المدرس", blank=True, null=True)
    teacher_email = models.EmailField(max_length=100, verbose_name="بريد المدرس الإلكتروني", unique=True) # البريد يجب أن يكون فريداً
    teacher_status = models.CharField(choices=STATUS_CHOICES, verbose_name="حالة المدرس")
    class Meta:
        verbose_name = "المدرس"
        verbose_name_plural = "المدرسين"
        ordering = ['teacher_name']

    def __str__(self):
        return self.teacher_name

# اليوم
class Today(models.Model):
    DAY_CHOICES = [
        ('1', 'السبت'),
        ('2', 'الأحد'),
        ('3', 'الاثنين'),
        ('4', 'الثلاثاء'),
        ('5', 'الأربعاء'),
        ('6', 'الخميس'),
        ('7', 'الجمعة'), # تم إضافة الجمعة للكمال
    ]
    day_name = models.CharField(max_length=10, choices=DAY_CHOICES, verbose_name="اسم اليوم")
    
    class Meta:
        verbose_name = "يوم"
        verbose_name_plural = "الأيام"
        # يمكن الترتيب حسب ID أو ترتيب مخصص للأيام، لكن مع choices يفضل الترتيب المخصص إذا أردت ترتيب أيام الأسبوع بشكل منطقي
        # للحفاظ على ترتيب أيام الأسبوع المنطقي، قد تحتاج لترتيب يدوي أو إضافة حقل ترتيب (ordinal)
        ordering = ['id'] 

    def __str__(self):
        return self.get_day_name_display() # استخدام get_FOO_display() لعرض الاسم الكامل

# الفترة (Period)
class Period(models.Model):
    PERIOD_CHOICES = [
        (1, "8:00 - 10:00"),
        (2, "10:00 - 12:00"),
        (3, "12:00 - 2:00"),
        (4, "2:00 - 4:00"),
        (5, "4:00 - 6:00"),
    ]
    period = models.IntegerField(choices=PERIOD_CHOICES, verbose_name="الفترة الزمنية")

    class Meta:
        verbose_name = "فترة"
        verbose_name_plural = "الفترات"
        ordering = ['period'] # ترتيب الفترات تصاعدياً

    def get_period_display(self):
        return dict(self.PERIOD_CHOICES).get(self.period, "غير معروف")

    def __str__(self):
        return f"الفترة: {self.get_period_display()}"


# وقت الدكتور (TeacherTime)
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
        ordering = ['fk_teacher__teacher_name', 'fk_today__id', 'fk_period__period']

    def __str__(self):
        return f"{self.fk_teacher.teacher_name} - {self.fk_today.day_name} - {self.fk_period.get_period_display()}"



# التوزيع (Distribution)
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

    class Meta:
        verbose_name = "توزيع"
        verbose_name_plural = "التوزيعات"
        unique_together = ('fk_group', 'fk_teacher', 'fk_subject') 
        ordering = ['fk_group__group_name', 'fk_subject__subject_name']

    def __str__(self):
        return f"المجموعة {self.fk_group.group_name} - الأستاذ {self.fk_teacher.teacher_name} - المادة {self.fk_subject.subject_name}"

# الجدول (Table)
class Table(models.Model):
    created_at = models.DateField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    table = models.FileField(max_length=100,upload_to="tables_file/", verbose_name="ملف الجدول")
    
    class Meta:
        verbose_name = "جدول"
        verbose_name_plural = "الجداول"
        ordering = ['-created_at'] # ترتيب حسب تاريخ الإنشاء تنازلياً

    def __str__(self):
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
    fk_teachertime = models.ForeignKey(
        TeacherTime, 
        on_delete=models.CASCADE, 
        related_name='lectures', 
        verbose_name="وقت الأستاذ"
    )
    fk_distribution = models.ForeignKey(
        Distribution, 
        on_delete=models.CASCADE, 
        related_name='lectures', 
        verbose_name="التوزيع"
    )

    class Meta:
        verbose_name = "محاضرة"
        verbose_name_plural = "المحاضرات"
        # يمكن إضافة unique_together إذا كانت هناك قيود إضافية
        # مثلاً: لا يمكن أن يكون في نفس القاعة، في نفس الجدول، في نفس وقت الأستاذ
        unique_together = ('fk_hall', 'fk_teachertime', 'fk_table')
        ordering = ['fk_table__created_at', 'fk_teachertime__fk_today__id', 'fk_teachertime__fk_period__period']


    def __str__(self):
        return f"محاضرة: {self.fk_distribution.fk_subject.subject_name} في {self.fk_hall.hall_name} - {self.fk_teachertime.fk_today.day_name} {self.fk_teachertime.fk_period.get_period_display()}"

