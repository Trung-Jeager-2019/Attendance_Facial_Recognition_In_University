fileName_AttendanceFiles = "AttendanceFiles/" + "INF0324" + "/" + "1" + "/" + "Attendance_" + "2020-06-17" + ".csv"
File_AttendanceFiles = open(fileName_AttendanceFiles,'rU')

List_Attendance = []

for line in File_AttendanceFiles:
    cells = line.split(",")
    if cells[0] == 'Id':
        continue
    else:
        List_Attendance.append(cells)

File_AttendanceFiles.close()

# print('List_Attendance: ', List_Attendance)
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

# print(List_Student)
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
# print(Dir_Attendance)

for Student in List_Student:
    if Student[0] in Dir_Attendance.keys():
        # print('--', Dir_Attendance[Student[0]][0])

        Id_Attendance.append(Dir_Attendance[Student[0]][0])
        Name_Attendance.append(Dir_Attendance[Student[0]][1])

        # Xử lý lấy họ tên từ DB
        # FullName = Student.objects.filter(id_student=str(cells[0]))
        # Name_Attendance.append(FullName[0].full_name_student)
        
        Date_Attendance.append(Dir_Attendance[Student[0]][2])
        Time_Attendance.append(Dir_Attendance[Student[0]][3])
        Status_Attendance.append('P')
    else:
        # print('--', Student)

        Id_Attendance.append(Student[0])
        Name_Attendance.append(Student[1])

        # Xử lý lấy họ tên từ DB
        # FullName = Student.objects.filter(id_student=str(cells[0]))
        # Name_Attendance.append(FullName[0].full_name_student)
        
        Date_Attendance.append("--/--/--")
        Time_Attendance.append("--:--:--")
        Status_Attendance.append('A')

table_attendance = list(zip(Numerical_order, Id_Attendance, Name_Attendance, Date_Attendance, Time_Attendance, Status_Attendance))

# print(table_attendance)


import os
path = "TrainingImage/" + "INF0464" + "/" + "1"

imagePaths = [os.path.join(path, f) for f in os.listdir(path)]

# print(imagePaths)

# -----------------------------------------------------------------------------------------------------------------
sem = '1'
dept = 'INF0464'

DIR = "AttendanceFiles" + os.sep + dept + os.sep + sem + os.sep

Attendance_List_Search = [length for length in os.listdir(DIR) if os.path.isfile(os.path.join(DIR,length))]
Date_List_Search = []

for Date_Search in Attendance_List_Search:
    Date_List_Search.append(Date_Search.split('_', 1)[1].split('.', 1)[0])
# print(Date_List_Search)

# -----------------------------------------------------------------------------------------------------------------
# Danh sách buổi đã đi / Danh sách số buổi đã học

Department_Of_Student = [['INF0324', '1', '2020-06-17', '10:27:25'], ['INF0324', '2', '2020-06-17', '16:32:45']]

# Danh sách số buổi đã học -> Buổi - ngày
dept = 'INF0324'
Attendance_Of_Student = {}
Total_Department = 0
for count in range(1, 4):
    DIR = "AttendanceFiles" + os.sep + dept + os.sep + str(count) + os.sep
    Attendance_List_Search = [length for length in os.listdir(DIR) if os.path.isfile(os.path.join(DIR,length))]
    Total_Department += len(Attendance_List_Search)
    
    if len(Attendance_List_Search) is not 0:
        List_Attendance = []
        for Date_Attendance in Attendance_List_Search:
            List_Attendance.append(Date_Attendance.split('_', 1)[1].split('.', 1)[0])
            
        Attendance_Of_Student[count] = List_Attendance
    else:
        continue

    # print(Attendance_Of_Student)

Date_Session_Of_Student = {}

for Date_Session in Department_Of_Student:
  if int(Date_Session[1]) not in Date_Session_Of_Student.keys():
    Date_Session_Of_Student[int(Date_Session[1])] = []
  Date_Session_Of_Student[int(Date_Session[1])].append(Date_Session[2])
  #print(str(Date_Session[1]) + '---' + str(Date_Session_Of_Student[int(Date_Session[1])]))

# print(Date_Session_Of_Student)

Numerical_order = list(range(1, Total_Department + 1))
Sessions_Attendance = []
Date_Attendance = []
Time_Attendance = []
Status_Attendance = []

for key in Attendance_Of_Student.keys():
  # print(key)
  if key in Date_Session_Of_Student.keys():
    # Tồn tại buổi học và ngày
    for Date_ in Attendance_Of_Student[key]:
      if Date_ in Date_Session_Of_Student[key]:
        # print("Có", Date_)
        Sessions_Attendance.append(key)
        Date_Attendance.append(Date_)
        for Time_ in Department_Of_Student:
          if str(Time_[1]) == str(key) and str(Time_[2]) == str(Date_):
            Time_Attendance.append(Time_[3])
        Status_Attendance.append('Có')
      else:
        Sessions_Attendance.append(key)
        Date_Attendance.append(Date_)
        Time_Attendance.append("--:--:--")
        Status_Attendance.append('Vắng')
  else:
    # Không tồn tại buổi học vs ngày
    for Date_ in Attendance_Of_Student[key]:
        # print("Vắng")
        # print("key vắng ", key)
        Sessions_Attendance.append(key)
        Date_Attendance.append(Date_)
        Time_Attendance.append("--:--:--")
        Status_Attendance.append('Vắng')

# print(list(zip(Sessions_Attendance, Date_Attendance, Time_Attendance, Status_Attendance)))
# -----------------------------------------------------------------------------------------------------------------

def remove_all_image(path, length_path): # ------------- Chưa hoàn thành
    count = 0
    for name_image in os.listdir(path + '/'):
        count += 1
        if name_image.endswith('.jpg'):
            remove_img('Image' + str(count) +'.jpg')
            if count == length_path:
                break
    return True

def remove_img(img_name):
    os.remove(img_name)
    # check if file exists or not
    if os.path.exists(img_name) is false:
        # file did not exists
        return True

Image_List = [file for file in os.listdir('ImagesUnknown/') if file.endswith('.jpg')]
remove_all_image('ImagesUnknown/', len(Image_List))
print(Image_List)
