from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, HttpResponse
from ..decorators import teacher_required
from ..forms import  TeacherSignUpForm
from ..models import User, DEPT, SEM, Student, Attendance
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.shortcuts import render
from attendance.models import DEPT, SEM, Student, Attendance
from PIL import Image, ImageTk
from unidecode import unidecode
import os, os.path
import pandas as pd
import numpy as np
import shutil
import json
import cv2
import csv
import glob
import datetime
import time

# Create your views here.

@teacher_required
def index(request):
    context = {
        'depts' : DEPT.objects.all(),
        'sems' : SEM.objects.all()
    }
    return render(request, 'classroom/teachers/attendance.html', context = context)

@teacher_required
def add_student(request):
    context = {
        'ids': Student.objects.all(),
        'depts' : DEPT.objects.all(),
    }
    return render(request, 'classroom/teachers/add_student.html', context = context)


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False


def checkId(Id, dept, sem):

    print("ID: ", Id)

    fileName = 'StudentDetails' + os.sep + dept + os.sep + sem + os.sep + 'StudentDetails.csv'
    # file1=pd.read_csv(fileName)
    Ids = []
    File_student = open(fileName,'rU')
    
    for Student in File_student:
        cells = Student.split(",")
        Ids.append(cells[0])
    File_student.close()
    
    if Id in Ids:
        return False
    else:
        return True


@teacher_required
def dataset_creator(request):
    if request.method == 'POST':
        check_id_student = request.POST['ID'].split(" ", 1)[0]
        check_department = request.POST['DEPT'].split(" ", 1)[0]
        warning_messenger = ""

        if check_id_student == "--" and check_department == "--":
            warning_messenger += "mã số sinh viên, môn học"
            messages.success(request, f'Vui lòng chọn ' +
                             warning_messenger + '!')
            context = {
                'ids': Student.objects.all(),
                'depts': DEPT.objects.all()
            }
            return render(request, 'classroom/teachers/add_student.html', context=context)
        else:
            if check_id_student == "--":
                warning_messenger += "mã số sinh viên"
                messages.success(request, f'Vui lòng chọn ' +
                                 warning_messenger + '!')
                context = {
                    'ids': Student.objects.all(),
                    'depts': DEPT.objects.all()
                }
                return render(request, 'classroom/teachers/add_student.html', context=context)
            if check_department == "--":
                warning_messenger += "môn học"
                messages.success(request, f'Vui lòng chọn ' +
                                 warning_messenger + '!')
                context = {
                    'ids': Student.objects.all(),
                    'depts': DEPT.objects.all()
                }
                return render(request, 'classroom/teachers/add_student.html', context=context)
        id_student = request.POST['ID'].split(' ', 1)[0]
        full = str(request.POST['ID'].split(' ', 2)[2])
        fullname_student = str(request.POST['ID'].split(' ', 2)[2])[::-1]
        name_student = unidecode(str(fullname_student.split(' ')[0])[::-1])
        
        print(id_student + " - " + fullname_student)

        dept = request.POST['DEPT'].split(' ', 1)[0]
        dept_name = request.POST['DEPT'].split('-', 1)[1]
        print(dept)
        
        if is_number(id_student) and name_student.isalpha():
            if checkId(id_student, dept, str(1)):
                cam = cv2.VideoCapture(0)
                
                harcascadePath = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
                detector = cv2.CascadeClassifier(harcascadePath)

                sampleNum = 0
                while(True):
                    ret, img = cam.read()
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    faces = detector.detectMultiScale(gray, 1.3, 5)
                    for (x,y,w,h) in faces:
                        
                        cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)        

                        sampleNum = sampleNum + 1
                        for count in range(1, 4):
                            cv2.imwrite("TrainingImage" + os.sep + dept + os.sep + str(count) + os.sep +
                                        name_student + "." + id_student + '.' + str(sampleNum) + ".jpg", gray[y:y+h, x:x+w])

                        cv2.imshow('frame',img)

                    if cv2.waitKey(100) & 0xFF == ord('q'):
                        break

                    elif sampleNum == 60:
                        break
                cam.release()
                cv2.destroyAllWindows()
                row = [id_student , name_student]
                
                for count in range(1, 4):
                    with open('StudentDetails' + os.sep + dept + os.sep + str(count) + os.sep + 'StudentDetails.csv', 'a+') as csvFile:
                        writer = csv.writer(csvFile)
                        writer.writerow(row)
                    csvFile.close()
                response = redirect('teachers:attendance_add_student')
                
            else:
                text_error = []
                text_error.append('- Sinh viên: ' + id_student + " - " + full + ' đã có trong cơ sở dữ liệu môn ' + dept_name)
                context = {
                    'code_error': 'Error 404.14. Lỗi truy cập!.',
                    'text_error': text_error,
                }
                return render(request,'classroom/teachers/404_result.html', context=context)
        else:
            text_error = []
            if is_number(id_student):
                text_error.append('- Tên của bạn: ' + name_student + ' phải là kí tự')
            elif name_student.isalpha():
                text_error.append('- Mã số sinh viên: ' + id_student + ' phải là chữ số.')
            else:
                text_error.append('- Tên của bạn: ' + name_student + ' phải là kí tự')
                text_error.append('- Mã số sinh viên: ' + id_student + ' phải là chữ số.')
            context = {
                'code_error': 'Error 404.5. Lỗi truy cập',
                'text_error': text_error,
            }
            return render(request,'classroom/teachers/404_result.html', context=context)
    return response


def getImagesAndLabels(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    faces = []
    Ids = []

    for imagePath in imagePaths:
        pilImage = Image.open(imagePath).convert('L')
        
        imageNp  =np.array(pilImage,'uint8')

        Id = int(os.path.split(imagePath)[-1].split(".")[1])
        
        faces.append(imageNp)
        
        Ids.append(Id)
    return faces, Ids


# def remove_img(img_name):
#     os.remove(img_name)
#     # check if file exists or not
#     if os.path.exists(img_name) is false:
#         # file did not exists
#         return True


# def remove_all_image(path, length_path): # ------------- Chưa hoàn thành
#     count = 0
#     for name_image in os.listdir(path + '/'):
#         count += 1
#         if name_image.endswith('.jpg'):
#             remove_img('Image' + str(count) +'.jpg')
#             if count == length_path:
#                 break

# def remove_all_image(path):
#     for i in glob.glob(path + '/' + '*.png'):
#         os.remove(i)


def trainer(dept, sem):

    # Delete all image
    # length_path = [file for file in os.listdir('ImagesUnknown/') if file.endswith('.jpg')]
    # print(length_path)
    # remove_all_image('ImagesUnknown', length_path)

    # recognizer =  cv2.face_LBPHFaceRecognizer.create()
    # recognizer = cv2.createLBPHFaceRecognizer()
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    
    harcascadePath = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(harcascadePath)
    for count in range(1, 4):
        faces, Id = getImagesAndLabels("TrainingImage" + os.sep + dept + os.sep + str(count))
        recognizer.train(faces, np.array(Id))
        recognizer.save("trainer" + os.sep + dept + os.sep + str(count) + os.sep + "Trainner.yml")
    print("Images Trained")


@teacher_required
def detector(request):
    if request.method == 'POST':

        check_department = request.POST['DEPT'].split(" ", 1)[0]
        check_session = request.POST['SEM'].split(" ", 1)[0]
        warning_messenger = ""

        if check_department == "--" and check_session == "--":
            warning_messenger += "môn học, buổi học"
            messages.success(request, f'Vui lòng chọn ' + warning_messenger + '!')
            context = {
                'depts': DEPT.objects.all(),
                'sems': SEM.objects.all()
            }
            return render(request, 'classroom/teachers/attendance.html', context=context)
        else:
            if check_department == "--":
                warning_messenger += "môn học"
                messages.success(request, f'Vui lòng chọn ' + warning_messenger + '!')
                context = {
                    'depts': DEPT.objects.all(),
                    'sems': SEM.objects.all()
                }
                return render(request, 'classroom/teachers/attendance.html', context=context)
            if check_session == "--":
                warning_messenger += "buổi học"
                messages.success(request, f'Vui lòng chọn ' + warning_messenger + '!')
                context = {
                    'depts': DEPT.objects.all(),
                    'sems': SEM.objects.all()
                }
                return render(request, 'classroom/teachers/attendance.html', context=context)
        
        dept = request.POST.get('DEPT').split(' ', 1)[0]
        sem = request.POST.get('SEM').split(' ', 1)[0]

        dept_name = request.POST.get('DEPT').split(' ', 2)[2]
        sem_name = request.POST.get('SEM').split(' ', 2)[2]
        print(dept_name)
        print(sem_name)

        trainer(dept, sem)
        
        # recognizer = cv2.face_LBPHFaceRecognizer.create()
        # recognizer = cv2.createLBPHFaceRecognizer()
        recognizer = cv2.face.LBPHFaceRecognizer_create()

        recognizer.read("trainer" + os.sep + dept + os.sep + sem + os.sep + "Trainner.yml")
        harcascadePath = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        faceCascade = cv2.CascadeClassifier(harcascadePath);
        df = pd.read_csv("StudentDetails" + os.sep + dept +
                         os.sep + sem + os.sep + "StudentDetails.csv")
        cam = cv2.VideoCapture(0)
        font = cv2.FONT_HERSHEY_SIMPLEX        
        col_names =  ['Id', 'Name', 'Date', 'Time']
        attendance = pd.DataFrame(columns = col_names)
# -----------------------------------------------------------------------------------------------------------------
        find_accuracy = []
        while True:
            ret, im = cam.read()
            gray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(gray, 1.2, 5)    

            for(x,y,w,h) in faces:
                cv2.rectangle(im, (x, y),(x+w, y+h),(225, 0, 0),2)
                Id, conf = recognizer.predict(gray[y:y+h, x:x+w])  
                                                
                if(conf < 68):

                    find_accuracy.append(100 - int(conf))
                    print('conf < 68 --> ' + str(100 - conf))

                    ts = time.time()
                    date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                    # print(date)
                    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                    # print(timeStamp)
                    aa = df.loc[df['Id'] == Id]['Name'].values
                    tt = str(Id) + "-" + str(aa)
                    attendance.loc[len(attendance)] = [Id, str(aa[0]), date, timeStamp]

                else:
                    Id = 'Unknown'                
                    tt = str(Id)  
                
                if(conf > 75): # 40

                    # find_accuracy.append(int(conf))
                    print('conf > 75 --> ' + str(conf))

                    noOfFile = len(os.listdir("ImagesUnknown")) + 1
                    cv2.imwrite("ImagesUnknown\Image" + str(noOfFile) + ".jpg", im[y : y+h,x : x+w])            
                cv2.putText(im, str(tt), (x, y+h), font, 1,(255, 255, 255), 2)  
                
            attendance = attendance.drop_duplicates(subset=['Id'], keep='first')
            
            cv2.imshow('im',im) 
            if (cv2.waitKey(1)==ord('q')):

                print("-> Độ chính xác thấp nhất: ", min(find_accuracy))
                print("-> Độ chính xác cao nhất: ", max(find_accuracy))
                break   

        ts = time.time()      
        date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        Hour, Minute, Second = timeStamp.split(":")

        fileName_AttendanceFiles = "AttendanceFiles" + os.sep + \
            dept + os.sep + sem + os.sep + "Attendance_" + date + ".csv"
        attendance.to_csv(fileName_AttendanceFiles, index=False)
# -----------------------------------------------------------------------------------------------------------------
        File_AttendanceFiles = open(fileName_AttendanceFiles,'rU')
        List_Attendance = []
        for line in File_AttendanceFiles:
            cells = line.split(",")
            if cells[0] == 'Id':
                continue
            else:
                List_Attendance.append(cells)
        
        total_present = len(List_Attendance)
        print("Student present: ", total_present)
        File_AttendanceFiles.close()
# -----------------------------------------------------------------------------------------------------------------
        fileName_StudentDetails = 'StudentDetails' + os.sep + dept + os.sep + sem + os.sep + 'StudentDetails.csv'
        File_StudentDetails = open(fileName_StudentDetails,'rU')
        List_Student = []
        for line in File_StudentDetails:
            cells = line.split(",")
            
            if cells[0].isalpha() or len(cells) == 1:
                continue
            else:
                List_Student.append(cells)

        total_student = len(List_Student)
        print("Student total: ", total_student)

        File_StudentDetails.close()
# -----------------------------------------------------------------------------------------------------------------
        Numerical_order = list(range(1, int(len(List_Student) + 1)))
        Id_Attendance = []
        Name_Attendance = []
        Date_Attendance = []
        Time_Attendance = []
        Status_Attendance = []

        Dir_Attendance = {}
        for Student_Attendance in List_Attendance:
            Dir_Attendance[Student_Attendance[0]] = Student_Attendance
        print(Dir_Attendance)

        for Student_ in List_Student:
            if Student_[0] in Dir_Attendance.keys():

                Id_Attendance.append(Dir_Attendance[Student_[0]][0])

                Full_Name = Student.objects.filter(id_student = Dir_Attendance[Student_[0]][0])
                Name_Attendance.append(Full_Name[0].full_name_student)
                
                Date_Attendance.append(Dir_Attendance[Student_[0]][2])
                Time_Attendance.append(Dir_Attendance[Student_[0]][3])

                Status_Attendance.append('Có mặt')

            else:

                Id_Attendance.append(Student_[0])

                Full_Name = Student.objects.filter(id_student = Student_[0])
                Name_Attendance.append(Full_Name[0].full_name_student)
                
                Date_Attendance.append("--/--/--")
                Time_Attendance.append("--:--:--")

                Status_Attendance.append('Vắng mặt')

        table_attendance = list(zip(Numerical_order, Id_Attendance, Name_Attendance, Date_Attendance, Time_Attendance, Status_Attendance))

        for student in table_attendance:
            if student[5] == 'P':
                id_student_attendance = student[1]
                date_attendance = student[3]
                time_attendance = student[4]
                check_student = len(Attendance.objects.filter(id_student = id_student_attendance, DEPT = dept, SEM = sem, date = date_attendance))
                if check_student is not 0:
                    print("ĐÃ CÓ TRONG CƠ SỞ DỮ LIỆU ĐIỂM DANH")
                else:
                    print("GIỪ THÊM VÀO CƠ SỞ DỮ LIỆU")
                    Attendance.objects.create(id_student = id_student_attendance, DEPT = dept, SEM = sem, date = date_attendance, time = time_attendance)
# -----------------------------------------------------------------------------------------------------------------
        cam.release()
        cv2.destroyAllWindows()

        length_lesson = 0
        for count in range(1, 4):
            DIR = "AttendanceFiles" + os.sep + dept + os.sep + str(count) + os.sep
            length_lesson += len([length for length in os.listdir(DIR) if os.path.isfile(os.path.join(DIR,length))])

        total_absent = total_student - total_present
        print("Student absent: ", total_absent)

        Statistical_total_present = int((total_present/total_student) * 100)
        Statistical_total_absent = int(100 - Statistical_total_present)

        context = {
            'Statistical_total_present': Statistical_total_present,
            'Statistical_total_absent': Statistical_total_absent,

            'table_attendance': table_attendance,
            'length_lesson': length_lesson,

            'total_present': total_present,
            'total_student': total_student,
            'total_absent': total_absent,

            'dept_name': dept_name,
            'sem_name': sem_name,
            'date': date,
        }
    return render(request,'classroom/teachers/result.html', context = context)


@teacher_required
def search_attendance(request):
    context = {
        'depts' : DEPT.objects.all(),
        'sems' : SEM.objects.all()
    }
    return render(request, 'classroom/teachers/search_attendance.html', context = context)

@teacher_required
def search_attendance_date(request):
    if request.method == 'POST':
        check_department = request.POST['DEPT'].split(" ", 1)[0]
        check_session = request.POST['SEM'].split(" ", 1)[0]
        warning_messenger = ""

        if check_department == "--" and check_session == "--":
            warning_messenger += "môn học, buổi học"
            messages.success(request, f'Vui lòng chọn ' +
                             warning_messenger + '!')
            context = {
                'depts': DEPT.objects.all(),
                'sems': SEM.objects.all()
            }
            return render(request, 'classroom/teachers/search_attendance.html', context=context)
        else:
            if check_department == "--":
                warning_messenger += "môn học"
                messages.success(request, f'Vui lòng chọn ' +
                                 warning_messenger + '!')
                context = {
                    'depts': DEPT.objects.all(),
                    'sems': SEM.objects.all()
                }
                return render(request, 'classroom/teachers/search_attendance.html', context=context)
            if check_session == "--":
                warning_messenger += "buổi học"
                messages.success(request, f'Vui lòng chọn ' +
                                 warning_messenger + '!')
                context = {
                    'depts': DEPT.objects.all(),
                    'sems': SEM.objects.all()
                }
                return render(request, 'classroom/teachers/search_attendance.html', context=context)
        Department_Search = request.POST.get('DEPT')
        Semester_Search = request.POST.get('SEM')

        dept_code = request.POST.get('DEPT').split(' ', 1)[0]
        sem_code = request.POST.get('SEM').split(' ', 1)[0]
        
        dept_name = request.POST.get('DEPT').split(' ', 2)[2]
        sem_name = request.POST.get('SEM').split(' ', 2)[2]

        print(Department_Search)
        print(Semester_Search)
        
        DIR = "AttendanceFiles" + os.sep + dept_code + os.sep + sem_code + os.sep
        Date_List_Search = []
        Attndance_List_Search = [length for length in os.listdir(DIR) if os.path.isfile(os.path.join(DIR,length))]
        if len(Attndance_List_Search) is 0:
            text_error = []
            text_error.append("- Môn \"" + dept_name + "\" buổi \"" + sem_name + "\" chưa có ngày học!")
            context = {
                'code_error': 'Error 404.0. Lỗi không tìm thấy!',
                'text_error': text_error,
            }
            return render(request, 'classroom/teachers/404_search.html', context = context)

        for Date_Search in Attndance_List_Search:
            Date_List_Search.append(Date_Search.split('_', 1)[1].split('.', 1)[0])

        print(Date_List_Search)

    context = {
        'dept' : Department_Search,
        'sem' : Semester_Search,
        'dates' : Date_List_Search,
    }
    return render(request, 'classroom/teachers/search_attendance_date.html', context = context)

@teacher_required
def search_attendance_details(request):
    if request.method == 'POST':
        
        dept = request.POST.get('DEPT').split(' ', 1)[0]
        sem = request.POST.get('SEM').split(' ', 1)[0]
        
        dept_name = request.POST.get('DEPT').split(' ', 2)[2]
        sem_name = request.POST.get('SEM').split(' ', 2)[2]
        print(dept_name)
        print(sem_name)
        
        format_date = request.POST.get('date').split('-')
        # list_date = datetime.datetime(int(format_date[0]), int(format_date[1]), int(format_date[2]))
        print(format_date)
        string_date = str(datetime.datetime(int(format_date[0]), int(format_date[1]), int(format_date[2])))
        date = string_date.split(' ', 1)[0]

        fileName_AttendanceFiles = "AttendanceFiles" + os.sep + \
            dept + os.sep + sem + os.sep + "Attendance_" + date + ".csv"
# -----------------------------------------------------------------------------------------------------------------
        File_AttendanceFiles = open(fileName_AttendanceFiles,'rU')
        List_Attendance = []
        for line in File_AttendanceFiles:
            cells = line.split(",")
            if cells[0] == 'Id':
                continue
            else:
                List_Attendance.append(cells)
        total_present = len(List_Attendance)
        print("Student present: ", total_present)
        
        File_AttendanceFiles.close()
# -----------------------------------------------------------------------------------------------------------------
        fileName_StudentDetails = 'StudentDetails' + os.sep + \
            dept + os.sep + sem + os.sep + 'StudentDetails.csv'
        File_StudentDetails = open(fileName_StudentDetails,'rU')
        List_Student = []
        for line in File_StudentDetails:
            cells = line.split(",")
            if cells[0].isalpha() or len(cells) == 1:
                continue
            else:
                List_Student.append(cells)

        total_student = len(List_Student)
        print("Student total: ", total_student)

        File_StudentDetails.close()
# -----------------------------------------------------------------------------------------------------------------
        Numerical_order = list(range(1, int(len(List_Student) + 1)))
        Id_Attendance = []
        Name_Attendance = []
        Date_Attendance = []
        Time_Attendance = []
        Status_Attendance = []

        Dir_Attendance = {}
        for Student_Attendance in List_Attendance:
            Dir_Attendance[Student_Attendance[0]] = Student_Attendance
        print(Dir_Attendance)

        for Student_ in List_Student:
            if Student_[0] in Dir_Attendance.keys():

                Id_Attendance.append(Dir_Attendance[Student_[0]][0])

                Full_Name = Student.objects.filter(id_student = Dir_Attendance[Student_[0]][0])
                Name_Attendance.append(Full_Name[0].full_name_student)
                
                Date_Attendance.append(Dir_Attendance[Student_[0]][2])
                Time_Attendance.append(Dir_Attendance[Student_[0]][3])

                Status_Attendance.append('Có mặt')

            else:

                Id_Attendance.append(Student_[0])

                Full_Name = Student.objects.filter(id_student = Student_[0])
                Name_Attendance.append(Full_Name[0].full_name_student)
                
                Date_Attendance.append("--/--/--")
                Time_Attendance.append("--:--:--")

                Status_Attendance.append('Vắng mặt')

        table_attendance = list(zip(Numerical_order, Id_Attendance, Name_Attendance, Date_Attendance, Time_Attendance, Status_Attendance))

        for student in table_attendance:
            if student[5] == 'P':
                id_student_attendance = student[1]
                date_attendance = student[3]
                time_attendance = student[4]
                Attendance.objects.create(id_student = id_student_attendance, DEPT = dept, SEM = sem, date = date_attendance, time = time_attendance)

        length_lesson = 0
        for count in range(1, 4):
            DIR = "AttendanceFiles" + os.sep + \
                dept + os.sep + str(count) + os.sep
            length_lesson += len([length for length in os.listdir(DIR) if os.path.isfile(os.path.join(DIR,length))])

        total_absent = total_student - total_present
        print("Student absent: ", total_absent)

        Statistical_total_present = int((total_present/total_student) * 100)
        Statistical_total_absent = int(100 - Statistical_total_present)

        context = {
            'Statistical_total_present': Statistical_total_present,
            'Statistical_total_absent': Statistical_total_absent,

            'table_attendance': table_attendance,
            'length_lesson': length_lesson,

            'total_present': total_present,
            'total_student': total_student,
            'total_absent': total_absent,

            'dept_name': dept_name,
            'sem_name': sem_name,
            'date': date,
        }

    return render(request, 'classroom/teachers/result.html', context = context)

