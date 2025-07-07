import pandas as pd
from ortools.sat.python import cp_model
from collections import defaultdict
from openpyxl.styles import Alignment, PatternFill, Font, Border, Side
from openpyxl import Workbook
import random
from .models import Department, Program, Hall, Level, Group, Subject, Teacher,Period,Today,TeacherTime, Distribution, Table
from collections import namedtuple

class TimeTableScheduler:
    def __init__(self):
        self.model                  = cp_model.CpModel() 
        self.solver                 = cp_model.CpSolver()

        self.available_times_df     =list(Period.objects.all())
        # self.periods                = Period.objects.all()
        self.professors              = {p.id: p for p in Teacher.objects.all()}
        self.courses                 = {c.id: c for c in Subject.objects.all()}
        self.rooms = list(Hall.objects.all())
        self.days = list(Today.objects.all())
        self.timesProfessor =list(TeacherTime.objects.all())
        self.teatchingGroups =list(Distribution.objects.all())
        self.programs = {p.id: p for p in Program.objects.all()}
        self.levels = {l.id: l for l in Level.objects.all()}
        self.groups = {g.id: g for g in Group.objects.all()}

        self.lecture_times          ={}   
        self.professoresdata        = []
        self.generated_schedule = []
        self.available_times        = {}


    def dicts_to_namedtuples(dict_list, typename="Row"):
        RowClass = namedtuple(typename, dict_list[0].keys())
        return [RowClass(**d) for d in dict_list]
    
    def add_data(self): 
        for row in self.available_times_df:
            time_from=row.period_from
            time_to=row.period_to
            time = f"{time_from}-{time_to}"
            self.available_times[row.pk]=time
        for tg in self.teatchingGroups:
            professor_id = tg.fk_teacher.id
            course_id = tg.fk_subject.id
            group_id = tg.fk_group.pk

            professor = self.professors[professor_id]
            course = self.courses[course_id]
            group = self.groups[group_id]
            level = self.levels[group.fk_level.pk]
            dept = self.programs[level.fk_program.pk]

            professor_times = [t for t in self.timesProfessor if t.fk_teacher.id == professor_id]

            availability = defaultdict(list)
            for t in professor_times:
                availability[t.fk_today.id].append(t.fk_period.pk)

            professordata = {
                "available": dict(availability),
                "name": professor.teacher_name.strip(),
                "ProfessorId": professor_id
            }

            self.professoresdata.append(professordata)

            self.lecture_times[tg.id] = {
                'course': course.subject_name.strip(),
                'teacher': professordata,
                'level': level.level_name.strip(),
                'dept': dept.program_name.strip(),
                'group': group.group_name.strip(),
                'std_count': group.number_students
            }
    def define_variables(self):
        self.schedule_vars = {}
        for course_id, course_info in self.lecture_times.items():
            for day in self.days: 
                for time_index in self.available_times_df:  
                    for room in self.rooms:  
                        var_name = f'course_{course_id}_day_{day.id}_time_{time_index.pk}_room_{room.hall_name}'
                        self.schedule_vars[(course_id, day.id, time_index.pk, room.hall_name)] = self.model.NewBoolVar(var_name)

    def add_constraints(self):
        self.add_courses_constraints()
        self.add_room_time_constraints()
        self.add_teacher_constraints()
        self.add_teacher_constraints_availability()
        self.add_dept_level_group_time_constraints()

    # قيد عدم تكرار المحاضرة في الاسبوع
    def add_courses_constraints(self):
        for course_id, course_info in self.lecture_times.items():
            course = []
            for day in self.days:
                for time_index in self.available_times_df:  
                    times=[]
                    for room in self.rooms:
                        course.append(self.schedule_vars[(course_id, day.id, time_index.pk, room.hall_name)])  
                        times.append(self.schedule_vars[(course_id, day.id, time_index.pk, room.hall_name)])
                    # self.model.Add(sum(times)<=1)  
            self.model.Add(sum(course) == 1)
    
    # قيد توزيع القاعات حسب السعة وبحيث لا تكرر المحاضره في اكثر من قاعة 
    def add_room_time_constraints(self):
        for day in self.days:
            for time_index in self.available_times_df:
                for row in self.rooms:
                    capacity=row.capacity_hall
                    room_name=row.hall_name
                    lectures_in_room=[]
                    for course_id, course_info in self.lecture_times.items():
                        student_count = course_info['std_count']
                        if student_count > capacity:
                            self.model.Add(self.schedule_vars[(course_id, day.id, time_index.pk, room_name)]==0)

                        lectures_in_room.append(self.schedule_vars[(course_id, day.id, time_index.pk, room_name)])
                    self.model.AddAtMostOne(lectures_in_room)

    # قيد عدم تكرار المدرس في نفس الوقت
    def add_teacher_constraints(self):
        for teacher_name in self.professoresdata:
            teacher_name = teacher_name['name']
            for day in self.days:
                for time_index in self.available_times_df:
                    lectures = []
                    for course_id, course_info in self.lecture_times.items():
                        if course_info['teacher']["name"] == teacher_name:
                            # print("========================= ",course_info['teacher']["name"])
                            for room in self.rooms:
                                lectures.append(self.schedule_vars[(course_id, day.id, time_index.pk, room.hall_name)])
                    self.model.Add(sum(lectures) <= 1) 

    # قيد تعيين المدرس في الاوقات المتاحة لة
    def add_teacher_constraints_availability(self):
        for course_id, course_info in self.lecture_times.items():
           available_times = course_info['teacher']["available"]
            # تكرار لكل مادة
           assigned_times = []  # قائمة لتخزين المتغيرات التي تخص تعيين الدكتور في هذه المادة
           for day in self.days:
              for time_index in self.available_times_df:
                  for room in self.rooms:
                     var = self.schedule_vars.get((course_id, day.id, time_index.pk, room.hall_name))                 
                     if day.id in available_times and time_index.pk in available_times[day.id]:
                        assigned_times.append(var)
           if assigned_times:
               self.model.Add(sum(assigned_times) >= 1)  # يجب أن يتم تعيينه على الأقل مرة واحدة للمادة  

 # إضافة قيود لمنع تكرار نفس القسم والمستوى والمجموعه في نفس الوقت
    def add_dept_level_group_time_constraints(self):
        # تجميع المواد حسب القسم والمستوى
        dept_level_courses = defaultdict(list)
        for course_id, course_info in self.lecture_times.items():
            key = (course_info['dept'], course_info['level'], course_info['group'])
            dept_level_courses[key].append(course_id)

        for (dept, level,group), courses in dept_level_courses.items():
            for day in self.days:
                for time_index in self.available_times_df:
                    time_slot_vars = []
                    for course_id in courses:
                        for room in self.rooms:
                            time_slot_vars.append(self.schedule_vars[(course_id, day.id, time_index.pk, room.hall_name)])
                    # لا يمكن جدولة أكثر من مادة لنفس القسم والمستوى في نفس الوقت
                    if time_slot_vars:
                        self.model.Add(sum(time_slot_vars) <= 1)
    
    # check conflicts after create schedule
    def check_conflicts(self, schedule):
        conflicts = []
        available_times_str = []
        for entry in schedule:
            day = entry["day"]
            day_id=entry["day_id"]
            time = entry["time"]
            doctor_name = entry["teatcher"]
            course = entry["course"]
            room=entry['room']
            std_count=entry['student_count']
            dept=entry['dept']
            level=entry['level']
            capacity=entry['capacity_room']
            available=entry['available']
            # print(f"day_id: {day_id} , available: {available}")
            # print("type of day_id:", type(day_id))
            # print("type of available:", type(available))
            if day_id not in available:
                for day_a, times in available.items():
                    
                    # day_name = self.days['Day Name'].loc[int(day_a)]
                    day_name = self.days[day_a].day_name
                    for time_idx in times:
                        time_slot = f"{day_name} {self.available_times[time_idx]}"
                        if time_slot not in available_times_str:
                            available_times_str.append(time_slot)
                conflicts.append({
                    'نوع التعارض': 'تم تعيين دكتور في غير موعدة',
                    'تفاصيل التعارض':f"اسم الدكتور: {doctor_name} , اليوم:{day} , الوقت: {time} الأوقات المتاحة: {available_times_str}"})

            if(std_count>capacity):
                conflicts.append({
                    'نوع التعارض': 'لم يتم تعين قاعة',
                    'تفاصيل التعارض':f'قسم: {dept} , مستوى:{level} , عدد الطلاب: {std_count} اكبر من {capacity} في قاعة :{room}'
                })
        return conflicts
    
    #save conflicts in file excel 
    def write_conflicts_to_excel(self, conflicts):
        if conflicts:
            # Create a new Excel writer object
            conflict_writer = pd.ExcelWriter('output/conflicts.xlsx', engine='openpyxl')
            
            # Convert conflicts to DataFrame
            conflict_df = pd.DataFrame(conflicts)
            
            # Write to Excel with Arabic column names
            conflict_df.to_excel(conflict_writer, sheet_name='تعارضات الدكاترة', index=False)
            
            # Get the worksheet
            worksheet = conflict_writer.sheets['تعارضات الدكاترة']
            
            # Format the worksheet
            for column in worksheet.columns:
                max_length = 0
                column = [cell for cell in column]
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
            # Save the conflicts Excel file
            conflict_writer.close()


    # check conflicts be create schedule
    def check_initial_conflicts(self):
        total_cells=len(self.available_times)*len(self.rooms)*len(self.days)
        total_lectures=len(self.lecture_times)
        conflicts = []
        # Group courses by professor
        professor_courses = {}
        # conflicts_room=[]
        max_capacity = max([c.capacity_hall for c in self.rooms])
    
        dept_level_courses = defaultdict(list)
        for course_id, course_info in self.lecture_times.items():
            key = (course_info['dept'], course_info['level'])
            std_count=course_info['std_count']
            dept_level_courses[key].append(std_count)
        
        for (dept, level), stdcount in dept_level_courses.items():
            if stdcount[0]>max_capacity:
                 conflicts.append({
                    'نوع التعارض': 'لم يتم تعين قاعة',
                    'تفاصيل التعارض':f'قسم: {dept} , مستوى:{level} , عدد الطلاب: {stdcount[0]} اكبر من {max_capacity} ',
                })
        
        for course_id, course_info in self.lecture_times.items():
            professor_name = course_info['teacher']['name']
            if professor_name not in professor_courses:
                professor_courses[professor_name] = []
            professor_courses[professor_name].append({
                'course': course_info['course'],
                'available_times': course_info['teacher']['available']
            })
        
        # Check conflicts for each professor
        for professor_name, courses in professor_courses.items():
            # Count total available time slots
            total_available_slots = 0
            available_times_str = []
            
            # Get all available time slots for this professor
            for course in courses:
                for day, times in course['available_times'].items():
                    # day_name = self.days['Day Name'].loc[int(day)]
                    day_name= self.days[day].day_name
                    for time_idx in times:
                        time_slot = f"{day_name} {self.available_times[time_idx]}"
                        if time_slot not in available_times_str:
                            available_times_str.append(time_slot)
                            total_available_slots += 1
            
            # Count number of courses
            num_courses = len(courses)
            # If professor has more courses than available time slots
            if num_courses > total_available_slots and total_available_slots!=0 :
                conflicts.append({
                    'نوع التعارض': 'عدد المواد أكثر من الأوقات المتاحة',
                    'تفاصيل التعارض':f'اسم الدكتور:{professor_name} ,عدد المواد:{str(num_courses)},عدد الأوقات المتاحة:{str(total_available_slots)}'
                })
            
            # If professor has no available times for some courses
            if total_available_slots == 0 and num_courses > 0:
                conflicts.append({
                    'نوع التعارض': 'لا يوجد أوقات متاحة',
                    'تفاصيل التعارض':f'اسم الدكتور:{professor_name} ,عدد المواد:{str(num_courses)},عدد الأوقات المتاحة:0'})
                
            if total_lectures>total_cells:
                  conflicts.append({
                    'نوع التعارض': 'لا يوجد قاعات كافيه ',
                    'تفاصيل التعارض':f' عدد المحاضرات كامله : {total_lectures} عدد الخلايا المتاحه في الجدول لاستيعاب المحاضرات : {total_cells}'})
                  break
            
        return conflicts
    

    @staticmethod
    def set_cell_border(cell):
        """
        تعيين الحدود لخلية معينة في Excel.
        """
        thin_border = Border(left=Side(style='thin'),
                             right=Side(style='thin'),
                             top=Side(style='thin'),
                             bottom=Side(style='thin'))
        cell.border = thin_border

    # save schedule in excel file
    def save_to_excel(self, schedule):
        wb = Workbook()
        ws = wb.active
        ws.title = "جدول المقررات الدراسية"
        rooms=[]
        for r in self.rooms:
            rooms.append(r.hall_name)
        headers = ['Day', 'Time'] + rooms 
        ws.append(headers)
        ws.row_dimensions[1].height = 80
        for cell in ws[1]:
            cell.font = Font(size=20,bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")  
            cell.alignment = Alignment(horizontal="center", vertical="center",)        
        
        schedule_by_day = defaultdict(list)
        for row in schedule:
            schedule_by_day[row['day']].append(row)
        # time_slots = ['08:00-10:00', '10:00-12:00', '12:00-02:00']

        row_num = 2  
        for day, rows in schedule_by_day.items():
            first_row = True  

            for slot_id,slot_value in self.available_times.items():
                if first_row:
                    ws[f'A{row_num}'] = day  
                ws[f'B{row_num}'] = slot_value

                added = False 
                for row in rows:
                    if row['time'] == slot_value:
                        for j, room in enumerate(self.rooms, start=2): 
                            if row['room'] == room.hall_name:  
                                # dept = row['Department'].split()
                                cell_value = f"{row['course']}\n{row['dept']}_{row['level']}_{row['group']}\n{row['teatcher']}"
                                ws.cell(row=row_num, column=j + 1, value=cell_value)
                                added = True
                if not added:
                    for j in range(2, len(self.rooms) + 2):  
                        ws.cell(row=row_num, column=j + 1, value="")

                first_row = False  
                for col in range(1, len(self.rooms) + 3):  
                    cell = ws.cell(row=row_num, column=col)
                    self.set_cell_border(cell)
                    
                    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                    cell.font = Font(name="Arial", size=20)
                    col_letter = ws.cell(row=1, column=col).column_letter  
                    ws.column_dimensions[col_letter].width = 30  
                row_num += 1
        wb.save('output/timetable.xlsx')
        print("📂 تم حفظ الجدول في 'timetable.xlsx'")    

    def solve(self):
        self.solver.parameters.random_seed=random.randint(1,10000)
        self.solver.parameters.enumerate_all_solutions=False
       
        status = self.solver.Solve(self.model)
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print("\n✅ تم إيجاد حل!\n")
            schedule = []
            for day in self.days:
                for time in self.available_times_df:
                    for room in self.rooms:
                        capacity=room.capacity_hall
                        room_name=room.hall_name
                        for course_id, course_info in self.lecture_times.items():
                            if self.solver.Value(self.schedule_vars[(course_id, day.id, time.pk, room_name)]) == 1:
                                id = time.pk
                                schedule.append({
                                    "day": day.day_name,
                                    "time": self.available_times[id],
                                    "room": room_name,
                                    "capacity_room":capacity,
                                    "course": course_info['course'],
                                    "teatcher": course_info['teacher']['name'],
                                    "available":course_info['teacher']['available'],
                                    "day_id":day.id,
                                    "group":course_info['group'],
                                    "level": course_info['level'],
                                    "dept": course_info['dept'],
                                    "student_count": course_info['std_count']
                                })

            if schedule:
                self.generated_schedule = schedule
                self.save_to_excel(schedule)
                conflicts = self.check_conflicts(schedule)
            
            # Write conflicts to Excel file
                self.write_conflicts_to_excel(conflicts)
            
                if conflicts:
                    print("\nتم العثور على تعارضات")
                else:
                    print("\n لا يوجد تعارضات")
        else:
            print("❌ لم يتم العثور على حل!")
            print("⚠ حاول تغيير القيود أو عدد القاعات المتاحة.")
            
            # Check for potential conflicts that might be preventing a solution
            initial_conflicts = self.check_initial_conflicts()
            if initial_conflicts:
                print("\nتم العثور على تعارضات محتملة   :")
                self.write_conflicts_to_excel(initial_conflicts)
                print("\n✅ تم حفظ التعارضات المحتملة في ملف 'conflicts.xlsx'")
            else:
                print("\nلم يتم العثور على تعارضات واضحة   ")
    def run(self):
        self.add_data()
        self.define_variables()
        self.add_constraints()
        self.solve()

