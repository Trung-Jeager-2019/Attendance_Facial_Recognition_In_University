fileName_AttendanceFiles = "AttendanceFiles/" + "INF0464" + "/" + "1" + "/" + "Attendance_" + "2020-06-05" + ".csv"
File_AttendanceFiles = open(fileName_AttendanceFiles,'rU')

List_Attendance = []

for line in File_AttendanceFiles:
    cells = line.split(",")
    if cells[0] == 'Id':
        continue
    else:
        List_Attendance.append(cells)

File_AttendanceFiles.close()

print(List_Attendance)
# -----------------------------------------------------------------------------------------------------------------
fileName_StudentDetails = 'StudentDetails/' + "INF0464" + "/" + "1" + "/" + 'StudentDetails.csv'
File_StudentDetails = open(fileName_StudentDetails,'rU')

List_Student = []

for line in File_StudentDetails:
    cells = line.split(",")
    
    if cells[0].isalpha() or len(cells) == 1:
        continue
    else:
        List_Student.append(cells)

File_StudentDetails.close()

print(List_Student)
# -----------------------------------------------------------------------------------------------------------------
Numerical_order = list(range(1, int(len(List_Student) + 1)))
Id_Attendance = []
Name_Attendance = []
Date_Attendance = []
Time_Attendance = []
Status_Attendance = []

Dir_Attendance = {}
for Student in List_Attendance:
    Dir_Attendance[Student[0]] = Student
print(Dir_Attendance)

for Student in List_Student:
    if Student[0] in Dir_Attendance.keys():
        print('--', Dir_Attendance[Student[0]][0])

        Id_Attendance.append(Dir_Attendance[Student[0]][0])
        Name_Attendance.append(Dir_Attendance[Student[0]][1])

        # Xử lý lấy họ tên từ DB
        # FullName = Student.objects.filter(id_student=str(cells[0]))
        # Name_Attendance.append(FullName[0].full_name_student)
        
        Date_Attendance.append(Dir_Attendance[Student[0]][2])
        Time_Attendance.append(Dir_Attendance[Student[0]][3])
        Status_Attendance.append('P')
    else:
        print('--', Student)

        Id_Attendance.append(Student[0])
        Name_Attendance.append(Student[1])

        # Xử lý lấy họ tên từ DB
        # FullName = Student.objects.filter(id_student=str(cells[0]))
        # Name_Attendance.append(FullName[0].full_name_student)
        
        Date_Attendance.append("--/--/--")
        Time_Attendance.append("--:--:--")
        Status_Attendance.append('A')

table_attendance = list(zip(Numerical_order, Id_Attendance, Name_Attendance, Date_Attendance, Time_Attendance, Status_Attendance))

print(table_attendance)


import os
path = "TrainingImage/" + "INF0464" + "/" + "1"

imagePaths = [os.path.join(path, f) for f in os.listdir(path)]

print(imagePaths)
