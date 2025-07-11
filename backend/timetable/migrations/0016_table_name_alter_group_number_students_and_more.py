# Generated by Django 5.2.3 on 2025-07-05 20:14

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0015_alter_subject_options_remove_subject_fk_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='table',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='اسم الجدول'),
        ),
        migrations.AlterField(
            model_name='group',
            name='number_students',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='عدد الطلاب'),
        ),
        migrations.AlterField(
            model_name='hall',
            name='capacity_hall',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='سعة القاعة'),
        ),
        migrations.AlterField(
            model_name='hall',
            name='hall_name',
            field=models.CharField(max_length=50, unique=True, verbose_name='اسم القاعة'),
        ),
        migrations.AlterField(
            model_name='hall',
            name='hall_status',
            field=models.CharField(choices=[('متاحة', 'متاحة'), ('تحت الصيانة', 'تحت الصيانة')], default='متاحة', verbose_name='حالة القاعة'),
        ),
        migrations.AlterField(
            model_name='level',
            name='number_students',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='عدد الطلاب'),
        ),
        migrations.AlterField(
            model_name='period',
            name='period',
            field=models.IntegerField(choices=[(1, '8:00 - 10:00'), (2, '10:00 - 12:00'), (3, '12:00 - 2:00'), (4, '2:00 - 4:00'), (5, '4:00 - 6:00')], unique=True, verbose_name='الفترة الزمنية'),
        ),
        migrations.AlterField(
            model_name='today',
            name='day_name',
            field=models.CharField(choices=[('1', 'السبت'), ('2', 'الأحد'), ('3', 'الاثنين'), ('4', 'الثلاثاء'), ('5', 'الأربعاء'), ('6', 'الخميس'), ('7', 'الجمعة')], max_length=10, unique=True, verbose_name='اسم اليوم'),
        ),
        migrations.AlterUniqueTogether(
            name='group',
            unique_together={('group_name', 'fk_level')},
        ),
        migrations.AlterUniqueTogether(
            name='lecture',
            unique_together={('fk_distribution', 'fk_teachertime', 'fk_table'), ('fk_hall', 'fk_teachertime', 'fk_table')},
        ),
        migrations.AlterUniqueTogether(
            name='level',
            unique_together={('level_name', 'fk_program')},
        ),
        migrations.AlterUniqueTogether(
            name='program',
            unique_together={('program_name', 'fk_department')},
        ),
    ]
